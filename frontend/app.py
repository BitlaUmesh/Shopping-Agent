"""
Streamlit Frontend
User interface for the AI-Driven Product Price Comparison System
"""

import streamlit as st
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path.parent))

from backend.app import PriceComparisonApp

from backend.config import config

# Page configuration
st.set_page_config(
    page_title="AI Price Comparison",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    .product-card {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        margin: 1rem 0;
        background-color: #f9f9f9;
    }
    .price-tag {
        font-size: 1.5rem;
        font-weight: bold;
        color: #2ecc71;
    }
    .rating {
        color: #f39c12;
    }
    .stButton>button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if 'app' not in st.session_state:
        st.session_state.app = None
    if 'product_info' not in st.session_state:
        st.session_state.product_info = None
    if 'recommendation' not in st.session_state:
        st.session_state.recommendation = None
    if 'results' not in st.session_state:
        st.session_state.results = []
    if 'shopping_chat_history' not in st.session_state:
        st.session_state.shopping_chat_history = []
    if 'research_chat_history' not in st.session_state:
        st.session_state.research_chat_history = []
    if 'search_performed' not in st.session_state:
        st.session_state.search_performed = False


def initialize_app():
    """Initialize the application."""
    if st.session_state.app is None:
        try:
            with st.spinner("Initializing AI system..."):
                st.session_state.app = PriceComparisonApp()
            st.success("✅ System initialized!")
        except Exception as e:
            st.error(f"❌ Initialization failed: {e}")
            st.info("Please check your .env file and API keys.")
            return False
    return True


def display_header():
    """Display the application header."""
    st.markdown('<div class="main-header">🛒 AI Price Comparison</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-header">Find the best deals with AI-powered product search</div>',
        unsafe_allow_html=True
    )


def search_interface():
    """Display the search interface."""
    st.markdown("## 🔍 Product Search")
    
    # Search input
    user_query = st.text_input(
        "What product are you looking for?",
        placeholder="e.g., Find the cheapest iPhone 15 128GB in India with fast delivery",
        key="product_query"
    )
    
    # Example queries
    with st.expander("💡 Example Queries"):
        examples = [
            "Find the cheapest iPhone 15 128GB in India",
            "Samsung Galaxy S23 under 50000 rupees with good ratings",
            "Best gaming laptop under $1500 with fast delivery",
            "Sony WH-1000XM5 headphones best price",
        ]
        for example in examples:
            if st.button(example, key=f"example_{examples.index(example)}"):
                st.session_state.product_query = example
                st.rerun()
    
    # Search button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        search_button = st.button("🔎 Search Products", type="primary", use_container_width=True)
    
    # Process search
    if search_button and user_query:
        with st.spinner("Searching for the best deals..."):
            # Progress bar
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(step: str, progress: int):
                progress_bar.progress(progress)
                status_text.text(step)
            
            try:
                # Perform search
                product_info, recommendation, results = st.session_state.app.process_query(
                    user_query,
                    progress_callback=update_progress
                )
                
                # Store results
                st.session_state.product_info = product_info
                st.session_state.recommendation = recommendation
                st.session_state.results = results
                st.session_state.search_performed = True
                
                # Clear progress
                progress_bar.empty()
                status_text.empty()
                
                st.success("✅ Search complete!")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Search failed: {e}")
                progress_bar.empty()
                status_text.empty()


def display_results():
    """Display search results."""
    if not st.session_state.search_performed:
        return
    
    recommendation = st.session_state.recommendation
    results = st.session_state.results
    
    if recommendation.get("status") == "no_results":
        st.warning("😔 No products found matching your criteria. Try a different search.")
        return
    
    if recommendation.get("status") != "success":
        st.error("❌ Unable to generate recommendations. Please try again.")
        return
    
    # Display recommendation analysis
    st.markdown("## 💡 AI Recommendation")
    
    analysis = recommendation.get("analysis", "")
    if analysis:
        st.info(analysis)
    
    # Display top recommendations
    st.markdown("### 🏆 Top Recommendations")
    
    products = recommendation.get("products", [])
    
    if not products:
        st.warning("No product recommendations available.")
        return
    
    # Display products in cards
    for i, product in enumerate(products[:5], 1):
        with st.container():
            st.markdown('<div class="product-card">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Product title
                st.markdown(f"### {i}. {product.get('title', 'N/A')}")
                
                # Price
                price_str = product.get('price_string', 'N/A')
                st.markdown(f'<div class="price-tag">💰 {price_str}</div>', unsafe_allow_html=True)
                
                # Seller and rating
                seller = product.get('seller', 'N/A')
                rating = product.get('rating', 'N/A')
                reviews = product.get('reviews', '')
                
                st.markdown(f"**Seller:** {seller}")
                if rating and rating != 'N/A':
                    st.markdown(f'<span class="rating">⭐ {rating}</span> {reviews}', unsafe_allow_html=True)
                
                # Delivery
                delivery = product.get('delivery', '')
                if delivery:
                    st.markdown(f"**Delivery:** {delivery}")
            
            with col2:
                # Thumbnail
                thumbnail = product.get('thumbnail', '')
                if thumbnail:
                    st.image(thumbnail, width=150)
                
                # Link
                url = product.get('url', '')
                if url:
                    st.link_button("🛒 View Product", url, use_container_width=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Show all results
    if len(results) > 5:
        with st.expander(f"📋 View All {len(results)} Results"):
            for i, product in enumerate(results, 1):
                st.markdown(f"{i}. **{product.get('title')}** - {product.get('price_string')} ({product.get('seller')})")


def shopping_assistant_interface():
    """Display shopping assistant chat interface."""
    if not st.session_state.search_performed:
        st.info("👆 Perform a product search first to chat with the Shopping Assistant.")
        return
    
    st.markdown("## 🤖 Shopping Assistant")
    st.markdown("Ask questions about the products, sellers, delivery, or any clarifications.")
    
    # Display chat history
    for message in st.session_state.shopping_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask the Shopping Assistant..."):
        # Add user message
        st.session_state.shopping_chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = st.session_state.app.chat_with_shopping_assistant(prompt)
            st.markdown(response)
        
        # Add assistant message
        st.session_state.shopping_chat_history.append({"role": "assistant", "content": response})
        st.rerun()


def research_assistant_interface():
    """Display research assistant chat interface."""
    st.markdown("## 🔬 Research Assistant")
    st.markdown("Get deep insights, comparisons, and product research with web search and database access.")
    
    # Display chat history
    for message in st.session_state.research_chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask the Research Assistant..."):
        # Add user message
        st.session_state.research_chat_history.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get assistant response
        with st.chat_message("assistant"):
            with st.spinner("Researching..."):
                response = st.session_state.app.chat_with_research_assistant(prompt)
            st.markdown(response)
        
        # Add assistant message
        st.session_state.research_chat_history.append({"role": "assistant", "content": response})
        st.rerun()


def sidebar():
    """Display sidebar with settings and information."""
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # Configuration status
        if config.validate():
            st.success("✅ Configuration Valid")
        else:
            st.error("❌ Invalid Configuration")
        
        st.markdown("### 🔧 Current Settings")
        st.markdown(f"**Model:** {config.GEMINI_MODEL}")
        st.markdown(f"**Region:** {config.DEFAULT_REGION}")
        st.markdown(f"**Currency:** {config.DEFAULT_CURRENCY}")
        st.markdown(f"**Max Results:** {config.MAX_RESULTS}")
        
        st.markdown("---")
        
        # Actions
        st.markdown("### 🎯 Actions")
        
        if st.button("🔄 New Search", use_container_width=True):
            st.session_state.search_performed = False
            st.session_state.product_info = None
            st.session_state.recommendation = None
            st.session_state.results = []
            st.session_state.shopping_chat_history = []
            st.rerun()
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.shopping_chat_history = []
            st.session_state.research_chat_history = []
            st.rerun()
        
        st.markdown("---")
        
        # Information
        st.markdown("### ℹ️ About")
        st.markdown("""
        This AI-powered system helps you find the best product deals by:
        - 🔍 Searching multiple sources
        - 🤖 AI-driven recommendations
        - 💬 Interactive assistants
        - 📊 Smart comparisons
        """)
        
        st.markdown("---")
        st.markdown("Made with ❤️ using Streamlit & Gemini")


def main():
    """Main application."""
    # Initialize
    init_session_state()
    
    # Display header
    display_header()
    
    # Initialize app
    if not initialize_app():
        return
    
    # Sidebar
    sidebar()
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Search", "🤖 Shopping Assistant", "🔬 Research Assistant"])
    
    with tab1:
        search_interface()
        display_results()
    
    with tab2:
        shopping_assistant_interface()
    
    with tab3:
        research_assistant_interface()


if __name__ == "__main__":
    main()