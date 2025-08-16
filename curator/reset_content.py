from profiles import ContentAccount

def reset_curators():
    """Reset all content curator accounts with their initial strategies"""
    
    # Alex - AI Breakthroughs Curator
    alex = ContentAccount.get("Alex")
    alex_strategy = """Focus on AI breakthroughs and cutting-edge research developments.
    
Key Areas:
- Latest research papers from top AI labs (OpenAI, DeepMind, Anthropic, Google Brain)
- Breakthrough algorithms and model architectures
- Novel AI capabilities and benchmark achievements  
- Scientific discoveries enabled by AI
- Technical deep-dives into new methodologies
- Analysis of research trends and future implications

Content Style:
- Technical but accessible explanations
- Focus on the "why this matters" angle
- Include expert commentary and analysis
- Cover both theoretical advances and practical implications
- Balance excitement with scientific rigor

Platforms Priority: Blog (60%), LinkedIn (25%), Newsletter (15%)
Target Audience: AI researchers, technical professionals, informed enthusiasts"""

    alex.reset(alex_strategy)
    alex.add_credits(50)  
    
    # Sam - Practical AI Tools Curator  
    sam = ContentAccount.get("Sam")
    sam_strategy = """Cover practical AI tools and applications that help businesses and individuals leverage AI technology.

Key Areas:
- New AI tool launches and updates (ChatGPT, Claude, Midjourney, etc.)
- Business automation and productivity applications
- AI-powered software and platforms
- Tutorials and how-to guides for AI tools
- ROI analysis and business case studies
- Tool comparisons and recommendations
- Implementation strategies for different industries

Content Style:
- Practical, actionable advice
- Clear step-by-step instructions
- Real-world examples and use cases
- Cost-benefit analysis
- User-friendly explanations
- Focus on immediate value and implementation

Platforms Priority: Twitter (40%), Blog (30%), LinkedIn (30%)
Target Audience: Business professionals, entrepreneurs, productivity enthusiasts, general users"""

    sam.reset(sam_strategy)
    sam.add_credits(75)  
    
    # Timi - AI Ethics & Policy Curator
    timi = ContentAccount.get("Timi") 
    timi_strategy = """Explore AI ethics, policy, regulation, and societal implications of artificial intelligence.

Key Areas:
- AI governance and regulatory developments
- Ethical considerations in AI development and deployment
- Bias, fairness, and accountability in AI systems
- Privacy and data protection issues
- AI safety and alignment research
- Social and economic impacts of AI
- Policy proposals and regulatory frameworks
- Industry self-regulation initiatives
- Global AI governance trends

Content Style:
- Balanced, thoughtful analysis
- Multi-stakeholder perspectives
- Policy implications and recommendations
- Accessible explanations of complex issues
- Evidence-based arguments
- Forward-looking analysis of trends

Platforms Priority: LinkedIn (50%), Blog (35%), Newsletter (15%)
Target Audience: Policy makers, business leaders, ethicists, concerned citizens, academics"""

    timi.reset(timi_strategy)
    timi.add_credits(60)  

if __name__ == "__main__":
    reset_curators()