import streamlit as st
import os
import json
import pandas as pd
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from bid_extractor import extract_all_bids, save_extracted_data
from bid_comparator import load_extracted_bids
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM for chat
llm = ChatOpenAI(temperature=0, model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))

# Chat prompt template
chat_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are a construction bid analysis expert. You have access to the following bid comparison data.

BID COMPARISON DATA:
{context}

USER QUESTION: {question}

INSTRUCTIONS:
1. Answer based ONLY on the provided data
2. If comparing plans, show exact prices from each file
3. Always explain WHY one bid is better (price difference, savings)
4. If asked about a specific plan, show all available prices
5. Use tables where helpful
6. Be specific with numbers - don't round off
7. If data is not available, clearly say so

ANSWER:
"""
)


def build_comparison_table(all_bids, fair_comparison=False):
    """
    Build a comparison table: Plan vs Files
    
    If fair_comparison=True, only include plans where 2+ files have data
    """
    
    # Collect all unique plans across all files
    all_plans = set()
    for file_name, plans in all_bids.items():
        for plan in plans:
            plan_num = plan.get("plan_number")
            if plan_num:
                all_plans.add(plan_num)
    
    all_plans = sorted(all_plans)
    
    # Build comparison data
    comparison_data = []
    skipped_plans = []
    
    for plan_num in all_plans:
        row = {"Plan": plan_num}
        prices = {}
        
        for file_name, plans in all_bids.items():
            # Find this plan in this file
            plan_data = next(
                (p for p in plans if p.get("plan_number") == plan_num), 
                None
            )
            
            if plan_data and plan_data.get("total_price"):
                price = plan_data["total_price"]
                row[file_name] = price
                prices[file_name] = price
            else:
                row[file_name] = None
        
        # Fair comparison: Skip if less than 2 files have data
        if fair_comparison and len(prices) < 2:
            skipped_plans.append(plan_num)
            continue
        
        # Determine winner (lowest price)
        if prices:
            winner = min(prices, key=prices.get)
            row["Winner"] = winner
            row["Best_Price"] = prices[winner]
        else:
            row["Winner"] = "N/A"
            row["Best_Price"] = None
        
        comparison_data.append(row)
    
    return pd.DataFrame(comparison_data), skipped_plans


def calculate_file_scores(comparison_df, all_bids):
    """
    Calculate which file wins overall
    """
    file_names = list(all_bids.keys())
    
    scores = {file: {
        "plans_won": 0,
        "plans_won_list": [],
        "total_if_chosen": 0,
        "plans_available": 0
    } for file in file_names}
    
    for _, row in comparison_df.iterrows():
        plan = row["Plan"]
        winner = row["Winner"]
        
        if winner != "N/A" and winner in scores:
            scores[winner]["plans_won"] += 1
            scores[winner]["plans_won_list"].append(plan)
        
        # Calculate totals for each file
        for file in file_names:
            if pd.notna(row.get(file)):
                scores[file]["total_if_chosen"] += row[file]
                scores[file]["plans_available"] += 1
    
    return scores


def generate_context_for_llm(all_bids, comparison_df, scores):
    """
    Generate a comprehensive context string for LLM
    """
    context_parts = []
    
    # File names
    context_parts.append("FILES ANALYZED:")
    for i, file_name in enumerate(all_bids.keys(), 1):
        context_parts.append(f"  {i}. {file_name}")
    context_parts.append("")
    
    # Plan-wise comparison
    context_parts.append("PLAN-BY-PLAN COMPARISON:")
    context_parts.append("-" * 50)
    
    for _, row in comparison_df.iterrows():
        plan = row["Plan"]
        winner = row["Winner"]
        context_parts.append(f"\nPlan {plan}:")
        
        for file_name in all_bids.keys():
            price = row.get(file_name)
            if pd.notna(price):
                marker = " ✓ LOWEST" if file_name == winner else ""
                context_parts.append(f"  - {file_name}: ${price:,.2f}{marker}")
            else:
                context_parts.append(f"  - {file_name}: N/A (no data)")
        
        if winner != "N/A":
            context_parts.append(f"  → Winner: {winner}")
    
    context_parts.append("")
    
    # File scores summary
    context_parts.append("FILE SCORES SUMMARY:")
    context_parts.append("-" * 50)
    
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]["plans_won"], reverse=True)
    
    for rank, (file_name, score) in enumerate(sorted_scores, 1):
        context_parts.append(f"\n#{rank} {file_name}")
        context_parts.append(f"  - Plans Won: {score['plans_won']}")
        context_parts.append(f"  - Win Rate: {score['plans_won']/len(comparison_df)*100:.1f}%")
        context_parts.append(f"  - Total Cost: ${score['total_if_chosen']:,.2f}")
        if score['plans_won_list']:
            context_parts.append(f"  - Won Plans: {', '.join(str(p) for p in score['plans_won_list'])}")
    
    # Overall winner
    context_parts.append("")
    context_parts.append("OVERALL WINNER:")
    context_parts.append(f"  {sorted_scores[0][0]} with {sorted_scores[0][1]['plans_won']} plans won")
    
    return "\n".join(context_parts)


def get_chat_response(context, question):
    """Get LLM response for chat"""
    prompt = chat_prompt.format(context=context, question=question)
    response = llm.invoke(prompt)
    return response.content

st.set_page_config(
    page_title="Bid Comparison Tool",
    page_icon="🏆",
    layout="wide"
)

st.title("🏆 Bid Comparison Tool")
st.markdown("Compare plans across multiple bid files and find the overall winner")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    data_folder = st.text_input("Data Folder", value="./data")
    
    st.markdown("---")
    
    # Extract button
    if st.button("🔄 Extract Data from Files", type="primary"):
        with st.spinner("Extracting plan data from all files... This may take a few minutes."):
            all_bids = extract_all_bids(data_folder)
            save_extracted_data(all_bids)
            st.session_state["all_bids"] = all_bids
            st.success(f"✅ Extracted data from {len(all_bids)} files!")
    
    st.markdown("---")
    
    # Load existing data
    if st.button("📂 Load Existing Data"):
        try:
            all_bids = load_extracted_bids()
            st.session_state["all_bids"] = all_bids
            st.session_state["fair_comparison"] = False  # Reset fair comparison mode
            st.success("✅ Loaded existing extracted data!")
        except FileNotFoundError:
            st.error("No extracted data found. Please extract first.")
    
    st.markdown("---")
    
    # Fair Comparison Button
    st.markdown("### 🎯 Fair Comparison Mode")
    st.caption("Sirf woh plans compare honge jahan 2+ files mein data ho")
    
    if st.button("⚖️ Re-evaluate (Fair Comparison)", type="secondary"):
        if "all_bids" in st.session_state:
            st.session_state["fair_comparison"] = True
            st.success("✅ Fair comparison mode ON! Sirf valid plans dikhenge.")
        else:
            st.error("Pehle data load karo!")

# Main content
if "all_bids" in st.session_state:
    all_bids = st.session_state["all_bids"]
    fair_mode = st.session_state.get("fair_comparison", False)
    
    # Build comparison
    comparison_df, skipped_plans = build_comparison_table(all_bids, fair_comparison=fair_mode)
    scores = calculate_file_scores(comparison_df, all_bids)
    
    # Show mode indicator
    if fair_mode:
        st.success(f"⚖️ **Fair Comparison Mode ON** - Sirf {len(comparison_df)} plans compare ho rahe hain (jahan 2+ files mein data hai)")
        if skipped_plans:
            with st.expander(f"⏭️ {len(skipped_plans)} plans skip kiye gaye (sirf 1 file mein data tha)"):
                st.write(", ".join(skipped_plans))
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["🏆 Winner", "📊 Plan Comparison", "📈 File Scores", "📄 Raw Data", "💬 Chat Mode"])
    
    # TAB 1: Winner
    with tab1:
        st.header("🏆 Overall Winner")
        
        # Sort by plans won
        sorted_scores = sorted(scores.items(), key=lambda x: x[1]["plans_won"], reverse=True)
        winner_file = sorted_scores[0][0]
        winner_score = sorted_scores[0][1]
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                label="🥇 Winner",
                value=winner_file[:30] + "..." if len(winner_file) > 30 else winner_file
            )
        
        with col2:
            st.metric(
                label="Plans Won",
                value=f"{winner_score['plans_won']} / {len(comparison_df)}"
            )
        
        with col3:
            win_rate = winner_score['plans_won'] / len(comparison_df) * 100
            st.metric(
                label="Win Rate",
                value=f"{win_rate:.1f}%"
            )
        
        st.markdown("---")
        
        # Winner details
        st.subheader("Winner Details")
        st.markdown(f"**File:** {winner_file}")
        st.markdown(f"**Plans Won:** {', '.join(winner_score['plans_won_list'])}")
        st.markdown(f"**Total Cost (if chosen):** ${winner_score['total_if_chosen']:,.2f}")
        
        # Savings comparison
        st.markdown("---")
        st.subheader("💰 Savings vs Other Bids")
        
        savings_data = []
        for file_name, score in sorted_scores[1:]:
            if score['total_if_chosen'] > 0:
                savings = score['total_if_chosen'] - winner_score['total_if_chosen']
                savings_data.append({
                    "Compared To": file_name,
                    "Their Total": f"${score['total_if_chosen']:,.2f}",
                    "Winner Total": f"${winner_score['total_if_chosen']:,.2f}",
                    "You Save": f"${savings:,.2f}"
                })
        
        if savings_data:
            st.table(pd.DataFrame(savings_data))
    
    # TAB 2: Plan Comparison
    with tab2:
        st.header("📊 Plan-by-Plan Comparison")
        
        # Format the dataframe for display
        display_df = comparison_df.copy()
        
        # Format price columns
        for col in display_df.columns:
            if col not in ["Plan", "Winner", "Best_Price"]:
                display_df[col] = display_df[col].apply(
                    lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A"
                )
        
        display_df["Best_Price"] = display_df["Best_Price"].apply(
            lambda x: f"${x:,.2f}" if pd.notna(x) else "N/A"
        )
        
        st.dataframe(display_df, width='stretch', height=500)
        
        # Download button
        csv = comparison_df.to_csv(index=False)
        st.download_button(
            label="📥 Download Comparison CSV",
            data=csv,
            file_name="bid_comparison.csv",
            mime="text/csv"
        )
    
    # TAB 3: File Scores
    with tab3:
        st.header("📈 File Scores Ranking")
        
        # Create ranking table
        ranking_data = []
        for rank, (file_name, score) in enumerate(sorted_scores, 1):
            ranking_data.append({
                "Rank": f"#{rank}",
                "File": file_name,
                "Plans Won": score['plans_won'],
                "Total Plans": len(comparison_df),
                "Win Rate": f"{score['plans_won']/len(comparison_df)*100:.1f}%",
                "Total Cost": f"${score['total_if_chosen']:,.2f}"
            })
        
        st.table(pd.DataFrame(ranking_data))
        
        # Bar chart
        st.subheader("Plans Won by File")
        chart_data = pd.DataFrame({
            "File": [s[0][:20] for s in sorted_scores],
            "Plans Won": [s[1]["plans_won"] for s in sorted_scores]
        })
        st.bar_chart(chart_data.set_index("File"))
    
    # TAB 4: Raw Data
    with tab4:
        st.header("📄 Raw Extracted Data")
        
        for file_name, plans in all_bids.items():
            with st.expander(f"📄 {file_name} ({len(plans)} plans)"):
                if plans:
                    st.dataframe(pd.DataFrame(plans), width='stretch')
                else:
                    st.warning("No plans extracted from this file")
    
    # TAB 5: Chat Mode
    with tab5:
        st.header("💬 Chat with Bid Data")
        st.markdown("Ask any question about the bids and get AI-powered answers!")
        
        st.markdown("---")
        
        # Example questions
        with st.expander("💡 Example Questions"):
            st.markdown("""
            - Plan 4101 kis file ka best hai aur kyun?
            - Compare plan 4102 across all files
            - Which file has the lowest prices overall?
            - What is the price difference for plan 4104 between files?
            - Summarize the winner for each plan
            - How much can I save by choosing the best bid?
            """)
        
        # Initialize chat history
        if "chat_history" not in st.session_state:
            st.session_state["chat_history"] = []
        
        # Generate context for LLM
        context = generate_context_for_llm(all_bids, comparison_df, scores)
        
        # Chat input
        user_question = st.text_input(
            "Ask your question:",
            placeholder="e.g., Plan 4104 kis bid ka best hai aur kyun?",
            key="chat_input"
        )
        
        col1, col2 = st.columns([1, 4])
        with col1:
            ask_btn = st.button("🔍 Ask", type="primary")
        with col2:
            clear_btn = st.button("🗑️ Clear Chat")
        
        if clear_btn:
            st.session_state["chat_history"] = []
            st.rerun()
        
        if ask_btn and user_question:
            with st.spinner("🤖 Thinking..."):
                response = get_chat_response(context, user_question)
            
            # Add to chat history
            st.session_state["chat_history"].append({
                "question": user_question,
                "answer": response
            })
        
        # Display chat history
        st.markdown("---")
        
        if st.session_state["chat_history"]:
            for i, chat in enumerate(reversed(st.session_state["chat_history"])):
                # Question
                st.markdown(f"**🧑 You:** {chat['question']}")
                
                # Answer
                st.markdown(f"**🤖 AI:**")
                st.markdown(chat['answer'])
                
                st.markdown("---")
        else:
            st.info("👆 Ask a question above to start chatting!")
        
        # Show context being used (collapsible)
        with st.expander("🔍 View Context Data (what AI sees)"):
            st.code(context, language="text")

else:
    st.info("👈 Use the sidebar to extract data from bid files or load existing data")
    
    st.markdown("""
    ### How to use:
    
    1. **Place your bid files** (PDF, Excel) in the `./data` folder
    2. **Click "Extract Data from Files"** to process all documents
    3. **View results** in the tabs:
       - 🏆 **Winner**: See which file wins overall
       - 📊 **Plan Comparison**: Compare each plan across files
       - 📈 **File Scores**: See ranking of all files
       - 📄 **Raw Data**: View extracted data
    
    ### What it does:
    
    - Extracts plan numbers and prices from each file using AI
    - Compares same plan across different bid files
    - Determines winner for each plan (lowest price)
    - Calculates overall winner (most plans won)
    - Shows savings compared to other bids
    """)

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit + LangChain + OpenAI*")