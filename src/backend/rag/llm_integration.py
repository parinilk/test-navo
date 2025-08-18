"""
LLM integration using OpenAI and LangChain for generating research responses
"""
import os
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

# Use direct OpenAI integration for now (LangChain has complex dependencies)
logging.info("Using direct OpenAI integration")

import openai

logger = logging.getLogger(__name__)

class LLMService:
    """Service for generating AI responses using OpenAI/LangChain"""
    
    def __init__(self):
        # Check for Azure OpenAI configuration first
        self.azure_api_key = os.getenv("AZURE_OPENAI_API_KEY")
        raw_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        
        # Clean the endpoint - handle different Azure endpoint formats
        if raw_endpoint:
            # Handle Azure AI Foundry endpoints (services.ai.azure.com)
            if "services.ai.azure.com" in raw_endpoint:
                # Use the endpoint as-is for Azure AI Foundry
                self.azure_endpoint = raw_endpoint
            # Handle standard Azure OpenAI endpoints (openai.azure.com)
            elif "/openai/deployments/" in raw_endpoint:
                # Extract just the base URL: https://resource.openai.azure.com/
                base_url = raw_endpoint.split("/openai/deployments/")[0] + "/"
                self.azure_endpoint = base_url
            else:
                # Use endpoint as-is if it's already clean
                self.azure_endpoint = raw_endpoint
        else:
            self.azure_endpoint = None
            
        self.azure_api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-15-preview")
        # Use AZURE_OPENAI_DEPLOYMENT_NAME for chat (not embeddings)
        self.azure_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        
        # Fallback to regular OpenAI
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        # Determine which service to use
        if self.azure_api_key and self.azure_endpoint and self.azure_deployment:
            self.use_azure = True
            logger.info("🔵 Using Azure OpenAI")
        elif self.openai_api_key:
            self.use_azure = False
            openai.api_key = self.openai_api_key
            logger.info("🟢 Using OpenAI")
        else:
            self.use_azure = False
            self.openai_api_key = "demo_mode"
            logger.warning("⚠️ No API keys found - using demo mode")
        
        # Use direct OpenAI integration
        self.use_langchain = False
        logger.info("✅ Direct OpenAI integration initialized")
        
        # System prompt based on your documentation
        self.system_prompt = self._create_system_prompt()
    
    def _create_system_prompt(self) -> str:
        """Create the system prompt based on Navo's requirements"""
        return """
### **🧾 Role**

You are Navo, an AI-powered research assistant specialized in the beauty and wellness industry.  
You can handle both SPECIFIC PRODUCT RESEARCH and GENERAL KNOWLEDGE QUESTIONS.
You assist professionals such as:

* Product developers  
* Brand managers  
* Regulatory and compliance specialists  
* Marketing strategists  
* Competitive intelligence and R&D teams

Your job is to analyze and respond to product-related research questions using a mix of:

* Retrieved product data (via RAG)  
* Your pretrained domain knowledge  
* External web search results (if available)

### **🎯 Task**

You support structured research across topics such as:

* Competitive Landscape Analysis  
* Pricing Strategy  
* Product Positioning / Claims Strategy  
* Marketing Channel Differentiation  
* Regulatory-Safe Ingredient Claims  
* Consumer Sentiment / Review Analysis  
* New Product Ideation  
* Line Extension / Format or Flavor Testing  
* Packaging Strategy (Image Upload Required)  
* White Label / ODM Brand Benchmarking

Your job is to:

1. Understand the user's question and infer intent when necessary  
2. Retrieve and synthesize relevant information from all available sources  
3. Return a complete answer with clear rationale, combining:  
   * Retrieved product data (structured and unstructured)  
   * Pretrained domain knowledge  
   * Public web or regulatory data (if provided)  
4. Label sources clearly and include a compliance disclaimer where appropriate  
5. Always provide deeper insights, not just shallow summaries

### **📤 Output Format**

Respond using this format:

`Answer:`  
`[Complete, helpful answer that combines retrieved data with context and external knowledge.]`

`Rationale:`  
`[Explain what you found in the data, what you added from external sources, and why.]`

`Sources Used:`  
`- Retrieved Product Data ✅`  
`- Pretrained Knowledge ✅ (if used)`  
`- Web Search ✅ (if used)`

`⚠️ Disclaimer:`  
`The information presented here is based on publicly available data sources (e.g., Health Canada, Walmart product listings, third-party reports).`    
`While we aim to provide accurate and helpful insights, this tool is not a substitute for legal, medical, or regulatory advice.`    
`Always consult qualified professionals before making product or compliance decisions.`

### **⛔ Constraints**

* Do NOT fabricate or infer beyond what is supported by available data  
* Avoid shallow summaries — your answers must demonstrate depth, evidence, and context  
* Label all sources clearly — show the difference between retrieved facts, general knowledge, and external sources  
* When a user asks a regulatory question, include the ⚠️ Disclaimer  
* Do not generalize regulatory conclusions unless the ingredient's use, form, and application context are clearly known (e.g., "rinse-off vs. leave-on")  
* If the dataset is insufficient, say so and suggest follow-up steps

### **🔍 Data Quality Assessment**

When retrieved product data lacks **critical information**, you MUST:
1. **Acknowledge the gap** - Say that data is incomplete, vague, or missing entirely
2. **Explain the impact** - Tell how missing info limits accuracy or certainty of the answer  
3. **Suggest next steps** - Offer alternatives, suggest what to look for, or recommend consulting experts
4. **Provide confidence assessment** - Indicate your confidence level in the analysis based on available data
"""
    
    async def generate_research_response(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None,
        product_data: List[Dict[str, Any]] = None,
        vector_results: List[Dict[str, Any]] = None,
        processed_query: Dict[str, Any] = None,
        web_search_results: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Generate a research response using LLM"""
        
        try:
            # Enhanced analysis for System Prompt compliance
            data_gaps = self._identify_data_gaps(product_data or [], processed_query or {})
            confidence_score = self._calculate_confidence_score(product_data or [], web_search_results or [], data_gaps)
            
            # Prepare context for the LLM
            llm_context = self._prepare_context(
                query=query,
                context=context,
                product_data=product_data or [],
                vector_results=vector_results or [],
                processed_query=processed_query or {},
                web_search_results=web_search_results or [],
                data_gaps=data_gaps,
                confidence_score=confidence_score
            )
            
            # Create the prompt
            if self.use_langchain:
                response = await self._generate_with_langchain(query, llm_context)
            else:
                response = await self._generate_with_openai(query, llm_context)
            
            # Parse the response
            parsed_response = self._parse_response(response)
            
            # Determine if disclaimer is needed
            needs_disclaimer = self._needs_regulatory_disclaimer(query, processed_query)
            if needs_disclaimer:
                parsed_response["disclaimer"] = self._get_regulatory_disclaimer()
            
            logger.info("✅ Generated LLM response successfully")
            return parsed_response
            
        except Exception as e:
            logger.error(f"❌ Error generating LLM response: {e}")
            # Return fallback response
            return self._create_fallback_response(query, str(e))
    
    def _prepare_context(
        self,
        query: str,
        context: Optional[Dict],
        product_data: List[Dict],
        vector_results: List[Dict],
        processed_query: Dict,
        web_search_results: List[Dict] = None,
        data_gaps: List[str] = None,
        confidence_score: float = 0.0
    ) -> str:
        """Prepare context string for LLM"""
        
        context_parts = []
        
        # Add user context
        if context:
            context_parts.append("**User Context:**")
            if "role" in context:
                context_parts.append(f"- Role: {context['role']}")
            if "objective" in context:
                context_parts.append(f"- Objective: {context['objective']}")
            if "topic" in context:
                context_parts.append(f"- Topic: {context['topic']}")
            context_parts.append("")
        
        # Add processed query info with enhanced analysis
        if processed_query:
            context_parts.append("**Query Analysis:**")
            context_parts.append(f"- Intent: {processed_query.get('intent', 'unknown')}")
            context_parts.append(f"- Analysis Complexity: {processed_query.get('analysis_complexity', 'unknown')}")
            
            if processed_query.get('categories'):
                context_parts.append(f"- Categories: {', '.join(processed_query['categories'])}")
            if processed_query.get('formats'):
                context_parts.append(f"- Formats: {', '.join(processed_query['formats'])}")
            if processed_query.get('brands'):
                context_parts.append(f"- Brands: {', '.join(processed_query['brands'])}")
            
            # Enhanced analysis fields
            if processed_query.get('functional_benefits'):
                context_parts.append(f"- Functional Benefits Sought: {', '.join(processed_query['functional_benefits'])}")
            if processed_query.get('ingredient_focus'):
                context_parts.append(f"- Ingredient Focus: {', '.join(processed_query['ingredient_focus'])}")
            if processed_query.get('regulatory_sensitive'):
                context_parts.append(f"- Regulatory Sensitive: {processed_query['regulatory_sensitive']}")
            if processed_query.get('data_requirements'):
                context_parts.append(f"- Data Requirements: {', '.join(processed_query['data_requirements'])}")
            
            context_parts.append("")
        
        # Add product data
        if product_data:
            context_parts.append("**Retrieved Product Data:**")
            for i, product in enumerate(product_data[:5]):  # Limit to first 5 products
                context_parts.append(f"{i+1}. **{product.get('product_name', 'Unknown Product')}**")
                if "brand" in product:
                    context_parts.append(f"   - Brand: {product['brand']}")
                if "category" in product:
                    context_parts.append(f"   - Category: {product['category']}")
                if "price" in product:
                    context_parts.append(f"   - Price: ${product['price']}")
                if "availability" in product:
                    context_parts.append(f"   - Availability: {product['availability']}")
                context_parts.append("")
        
        # Add vector search results if available
        if vector_results:
            context_parts.append("**Similar Products (Vector Search):**")
            for result in vector_results[:3]:  # Limit to top 3
                context_parts.append(f"- Similarity: {result.get('similarity_score', 0):.2f}")
                if "metadata" in result:
                    context_parts.append(f"  Metadata: {result['metadata']}")
            context_parts.append("")
        
        # Add web search results if available
        if web_search_results:
            context_parts.append("**Web Search Results:**")
            for i, result in enumerate(web_search_results[:5]):  # Limit to top 5
                context_parts.append(f"{i+1}. **{result.get('title', 'No title')}**")
                context_parts.append(f"   Source: {result.get('source', 'Unknown')}")
                if result.get('snippet'):
                    context_parts.append(f"   Summary: {result['snippet']}")
                if result.get('url'):
                    context_parts.append(f"   URL: {result['url']}")
                context_parts.append("")
        
        # Add data quality assessment (System Prompt compliance)
        if data_gaps or confidence_score:
            context_parts.append("**Data Quality Assessment:**")
            context_parts.append(f"- Analysis Confidence: {confidence_score:.2f} ({self._get_confidence_label(confidence_score)})")
            
            if data_gaps:
                context_parts.append("- Identified Data Gaps:")
                for gap in data_gaps:
                    context_parts.append(f"  • {gap}")
                context_parts.append("- Note: Analysis confidence reduced due to missing data")
            else:
                context_parts.append("- No critical data gaps identified")
            
            context_parts.append("")
        
        return "\n".join(context_parts)
    
    async def _generate_with_langchain(self, query: str, context: str) -> str:
        """Generate response using LangChain"""
        try:
            # Create prompt template
            messages = [
                SystemMessage(content=self.system_prompt),
                HumanMessage(content=f"Context:\n{context}\n\nQuery: {query}")
            ]
            
            # Generate response
            response = await self.chat_model.agenerate([messages])
            return response.generations[0][0].text
            
        except Exception as e:
            logger.error(f"LangChain generation failed: {e}")
            # Fallback to direct OpenAI
            return await self._generate_with_openai(query, context)
    
    async def _generate_with_openai(self, query: str, context: str) -> str:
        """Generate response using OpenAI or Azure OpenAI API"""
        try:
            # For testing without API key, return a mock response
            if self.openai_api_key == "demo_mode" or self.openai_api_key == "your_openai_api_key_here":
                return self._create_mock_response(query, context)
            
            if self.use_azure:
                # Use Azure OpenAI
                from openai import AzureOpenAI
                
                client = AzureOpenAI(
                    api_key=self.azure_api_key,
                    api_version=self.azure_api_version,
                    azure_endpoint=self.azure_endpoint
                )
                
                response = client.chat.completions.create(
                    model=self.azure_deployment,  # This is your deployment name
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"Context:\n{context}\n\nQuery: {query}"}
                    ],
                    temperature=0.3,
                    max_tokens=1500
                )
                
                logger.info(f"✅ Azure OpenAI response generated using deployment: {self.azure_deployment}")
                
            else:
                # Use regular OpenAI
                from openai import OpenAI
                client = OpenAI(api_key=self.openai_api_key)
                
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": self.system_prompt},
                        {"role": "user", "content": f"Context:\n{context}\n\nQuery: {query}"}
                    ],
                    temperature=0.3,
                    max_tokens=1500
                )
                
                logger.info("✅ OpenAI response generated")
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            # Return mock response for testing
            return self._create_mock_response(query, context)
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        
        # Simple parsing - you can make this more sophisticated
        sections = {
            "answer": "",
            "rationale": "",
            "sources_used": ["Retrieved Product Data ✅", "Pretrained Knowledge ✅"]
        }
        
        # Try to extract sections
        current_section = "answer"
        for line in response.split('\n'):
            line = line.strip()
            
            if line.lower().startswith("answer:"):
                current_section = "answer"
                line = line[7:].strip()
            elif line.lower().startswith("rationale:"):
                current_section = "rationale"
                line = line[10:].strip()
            elif line.lower().startswith("sources used:"):
                current_section = "sources"
                continue
            
            if line and current_section in ["answer", "rationale"]:
                if sections[current_section]:
                    sections[current_section] += " " + line
                else:
                    sections[current_section] = line
        
        # If parsing failed, use the whole response as answer
        if not sections["answer"]:
            sections["answer"] = response
            sections["rationale"] = "Generated comprehensive response based on available data and domain knowledge."
        
        return sections
    
    def _needs_regulatory_disclaimer(self, query: str, processed_query: Dict) -> bool:
        """Determine if regulatory disclaimer is needed"""
        regulatory_keywords = [
            "allowed", "permitted", "legal", "regulation", "compliance", 
            "banned", "restricted", "regulatory", "health canada", "fda"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in regulatory_keywords) or \
               processed_query.get("intent") == "regulatory_compliance"
    
    def _get_regulatory_disclaimer(self) -> str:
        """Get regulatory disclaimer text"""
        return """The information presented here is based on publicly available data sources (e.g., Health Canada, Walmart product listings, third-party reports). While we aim to provide accurate and helpful insights, this tool is not a substitute for legal, medical, or regulatory advice. Always consult qualified professionals before making product or compliance decisions."""
    
    def _create_mock_response(self, query: str, context: str) -> str:
        """Create mock response for testing without OpenAI API"""
        return f"""Answer:
Based on the available product data in the Navo database, I can provide insights about your query: "{query}".

The retrieved data shows various beauty and wellness products with detailed information including pricing, ingredients, and customer ratings. From the context provided, I can see products across categories like skincare serums, supplements, and wellness products.

Rationale:
This response is generated using the retrieved product data from MongoDB and vector similarity search results. The analysis combines structured product information with domain knowledge about the beauty and wellness industry.

Sources Used:
- Retrieved Product Data ✅
- Vector Search Results ✅
- Pretrained Knowledge ✅

Note: This is a demo response generated without OpenAI API. For full functionality, please configure your OpenAI API key."""

    def _create_fallback_response(self, query: str, error: str) -> Dict[str, Any]:
        """Create fallback response when LLM fails"""
        return {
            "answer": f"I apologize, but I encountered an issue processing your query: '{query}'. Please try rephrasing your question or contact support if the issue persists.",
            "rationale": f"Technical error occurred during response generation: {error}",
            "sources_used": ["Error Response"],
            "disclaimer": "This is an error response. Please try again or contact support.",
            "confidence_score": 0.0,
            "data_gaps": ["System error occurred"]
        }
    
    def _identify_data_gaps(self, product_data: List[Dict], processed_query: Dict) -> List[str]:
        """Identify missing data that affects analysis quality (System Prompt compliance)"""
        gaps = []
        
        # Check product data completeness
        if not product_data:
            gaps.append("No product data available for analysis")
            return gaps
        
        # Check for missing ingredient information
        products_without_ingredients = [p for p in product_data if not p.get('ingredients') and not p.get('description')]
        if products_without_ingredients:
            gaps.append(f"Ingredient information missing for {len(products_without_ingredients)} products")
        
        # Check for missing pricing data
        products_without_pricing = [p for p in product_data if not p.get('price')]
        if products_without_pricing:
            gaps.append(f"Pricing information missing for {len(products_without_pricing)} products")
        
        # Check for missing concentration data (regulatory sensitive)
        if processed_query.get('regulatory_sensitive'):
            gaps.append("Ingredient concentrations needed for regulatory analysis")
        
        # Check for specific data requirements
        data_requirements = processed_query.get('data_requirements', [])
        if 'ingredient_concentrations' in data_requirements:
            gaps.append("Detailed ingredient concentrations required")
        if 'pricing_per_serving' in data_requirements:
            gaps.append("Per-serving pricing calculations needed")
        if 'regulatory_compliance' in data_requirements:
            gaps.append("Regulatory compliance data required")
        
        return gaps
    
    def _calculate_confidence_score(self, product_data: List[Dict], web_search_results: List[Dict], data_gaps: List[str]) -> float:
        """Calculate confidence score for analysis (System Prompt compliance)"""
        base_confidence = 1.0
        
        # Deduct for missing product data
        if not product_data:
            return 0.1
        
        # Deduct for each data gap
        gap_penalty = len(data_gaps) * 0.15
        confidence = base_confidence - gap_penalty
        
        # Adjust for data completeness
        if product_data:
            # Check completeness of product data
            complete_products = 0
            for product in product_data:
                completeness = 0
                if product.get('product_name'): completeness += 1
                if product.get('brand'): completeness += 1
                if product.get('price'): completeness += 1
                if product.get('description'): completeness += 1
                if completeness >= 3: complete_products += 1
            
            completeness_ratio = complete_products / len(product_data)
            confidence *= completeness_ratio
        
        # Bonus for web search results
        if web_search_results:
            confidence += 0.1
        
        return max(0.0, min(1.0, confidence))
    
    def _get_confidence_label(self, confidence_score: float) -> str:
        """Get confidence label for score"""
        if confidence_score >= 0.8:
            return "High"
        elif confidence_score >= 0.6:
            return "Medium"
        elif confidence_score >= 0.4:
            return "Low"
        else:
            return "Very Low"
