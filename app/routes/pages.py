from fastapi import APIRouter, HTTPException, status
from app.models import (
    GeneratePageRequest,
    EditSectionRequest,
    ReorderSectionsRequest,
    PublishPageRequest,
    PageSpecResponse,
    PublishResponse
)
from app.llm.generator import generate_page_spec, regenerate_section
from app.db import save_page, get_page, update_page, publish_page, delete_page
from app.crawler import WebCrawler
import uuid
import logging

logger = logging.getLogger(__name__)
crawler = WebCrawler()

router = APIRouter()

@router.post("/pages/generate", response_model=PageSpecResponse)
async def generate_landing_page(request: GeneratePageRequest):
    """
    Generate a new landing page spec from user input
    Optionally crawls website to extract brand context
    
    Returns:
        PageSpecResponse: Generated page specification
    """
    try:
        user_input = {
            "industry": request.industry,
            "offer": request.offer,
            "target_audience": request.target_audience,
            "brand_tone": request.brand_tone
        }
        
        # Crawl website if URL provided
        crawled_context = None
        if request.website_url:
            logger.info(f"Crawling website: {request.website_url}")
            crawled_context = crawler.crawl_website(request.website_url)
            if crawled_context:
                logger.info("✓ Website crawled successfully")
            else:
                logger.warning("Website crawl failed, proceeding without brand context")
        
        # Generate page spec from LLM (with or without crawled context)
        page_spec = generate_page_spec(user_input, crawled_context)
        
        # Assign unique ID if not present
        if "pageId" not in page_spec:
            page_spec["pageId"] = f"landing-{uuid.uuid4().hex[:8]}"
        
        if "version" not in page_spec:
            page_spec["version"] = 1
        
        # Save to database WITH context (for regeneration)
        saved = save_page(
            page_spec,
            user_context=user_input,
            crawled_context=crawled_context
        )
        
        return PageSpecResponse(
            pageId=page_spec["pageId"],
            version=page_spec["version"],
            sections=page_spec["sections"]
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid request: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate landing page: {str(e)}"
        )
    
@router.get("/pages", response_model=list)
async def list_pages():
    """
    Retrieve all saved pages
    
    Returns:
        list: List of page summaries
    """
    try:
        from app.db import get_all_pages
        pages = get_all_pages()
        
        return [{
            "pageId": page["page_id"],
            "version": page["version"],
            "sectionCount": page["section_count"],
            "createdAt": page["created_at"].isoformat() if page.get("created_at") else None,
            "updatedAt": page["updated_at"].isoformat() if page.get("updated_at") else None,
            "published": page.get("published", False)
        } for page in pages]
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve pages: {str(e)}"
        )

@router.get("/pages/{page_id}", response_model=PageSpecResponse)
async def get_landing_page(page_id: str):
    """
    Retrieve a saved landing page
    
    Args:
        page_id: The page ID to retrieve
    
    Returns:
        PageSpecResponse: The page specification with user context
    """
    try:
        page = get_page(page_id)
        
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page {page_id} not found"
            )
        
        # Include user_context in the response
        response_data = {
            "pageId": page["page_id"],
            "version": page["version"],
            "sections": page["sections"]
        }
        
        # Add user_context if it exists
        if "user_context" in page and page["user_context"]:
            response_data["user_context"] = page["user_context"]
        
        return response_data
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve page: {str(e)}"
        )

@router.post("/pages/{page_id}/edit-section")
async def edit_section(page_id: str, request: EditSectionRequest):
    """
    Edit a specific section in a page
    
    Args:
        page_id: The page ID
        request: Updated section data
    
    Returns:
        dict: Updated page
    """
    try:
        page = get_page(page_id)
        
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page {page_id} not found"
            )
        
        # Find and update section
        sections = page["sections"]
        section_found = False
        
        for section in sections:
            if section["id"] == request.section_id:
                section["data"] = request.data
                section_found = True
                break
        
        if not section_found:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section {request.section_id} not found"
            )
        
        # Update in database
        updated_page = update_page(page_id, sections)
        
        return {
            "message": "Section updated successfully",
            "page_id": page_id,
            "version": updated_page["version"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to edit section: {str(e)}"
        )


@router.post("/pages/{page_id}/regenerate-section")
async def regenerate_section_endpoint(page_id: str, request: EditSectionRequest):
    """
    Regenerate a section using AI
    
    Args:
        page_id: The page ID
        request: Section ID and context
    
    Returns:
        dict: Updated page with regenerated section
    """
    try:
        page = get_page(page_id)
        
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page {page_id} not found"
            )
        
        # Find the section
        sections = page["sections"]
        section_to_regenerate = None
        
        for section in sections:
            if section["id"] == request.section_id:
                section_to_regenerate = section
                break
        
        if not section_to_regenerate:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Section {request.section_id} not found"
            )
        
        # Regenerate using LLM
        user_input = request.data.get("context", {})
        regenerated = regenerate_section(section_to_regenerate, user_input)
        
        # Update section in page
        for section in sections:
            if section["id"] == request.section_id:
                section["data"] = regenerated["data"]
                break
        
        # Save to database
        updated_page = update_page(page_id, sections)
        
        return {
            "message": "Section regenerated successfully",
            "page_id": page_id,
            "version": updated_page["version"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to regenerate section: {str(e)}"
        )


@router.post("/pages/{page_id}/reorder-sections")
async def reorder_sections(page_id: str, request: ReorderSectionsRequest):
    """
    Reorder sections in a page
    
    Args:
        page_id: The page ID
        request: New section order
    
    Returns:
        dict: Updated page
    """
    try:
        page = get_page(page_id)
        
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page {page_id} not found"
            )
        
        # Update order
        updated_page = update_page(page_id, request.sections)
        
        return {
            "message": "Sections reordered successfully",
            "page_id": page_id,
            "version": updated_page["version"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reorder sections: {str(e)}"
        )


@router.post("/pages/{page_id}/publish", response_model=PublishResponse)
async def publish_landing_page(page_id: str):
    """
    Publish a landing page
    
    Args:
        page_id: The page ID to publish
    
    Returns:
        PublishResponse: Confirmation and preview URL
    """
    try:
        page = get_page(page_id)
        
        if not page:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page {page_id} not found"
            )
        
        # Publish
        published_page = publish_page(page_id)
        
        return PublishResponse(
            page_id=page_id,
            version=published_page["version"],
            url=f"/preview/{page_id}",
            message="Page published successfully"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to publish page: {str(e)}"
        )


@router.delete("/pages/{page_id}")
async def delete_landing_page(page_id: str):
    """
    Delete a landing page
    
    Args:
        page_id: The page ID to delete
    
    Returns:
        dict: Confirmation
    """
    try:
        success = delete_page(page_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Page {page_id} not found"
            )
        
        return {"message": "Page deleted successfully", "page_id": page_id}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete page: {str(e)}"
        )