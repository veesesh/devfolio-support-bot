"""
Telegram Bot Command Responses
Contains preset answers for slash commands.
No bot logic here - just the response content.
"""

COMMAND_RESPONSES = {
    "start": """
👋 **Welcome to Devfolio Support Bot!**

I'm here to help answer questions about hackathons on Devfolio.

**Quick Commands:**
/help - Show all commands
/hackathon - About setting up hackathons
/judging - Judging process
/submission - Project submissions
/team - Team management
/tracks - Track and Prizes information
/support - Get additional help

""",
    
    "help": """
📚 **Available Commands:**

/hackathon - Learn about creating and joining hackathons
/judging - Understand the judging process
/submission - How to submit your project
/team - Creating and managing teams
/tracks - How to add tracks and prizes
/support - Get additional help

💡 You can also ask me any question directly, and I'll search our documentation!
""",
    
    "hackathon": """
🎯 **Hackathons on Devfolio**

**For Organizers:**

**Step 1: Get Started**
• Go to https://org.devfolio.co/ and click "Organize New"
• Select your hackathon type and fill out the required info

**Step 2: Provide Details**
• Name and Tagline
• Description
• Team Size
• Brand assets (with proper dimensions)
• Application dates
• Project submission dates

**Step 3: Submit for Verification**
• Complete all details to reach 100% completion
• Click "Submit for Verification"
• Our team will review and get back to you within 24 hours or less to get your hackathon live!

Need more help? Ask me specific questions or use /support
""",
    
    "judging": """
⚖️ **Judging Process**

Let the organiser know if you want to set the judging for your hackathon and let them enable it based on your requirements. In the meantime, here's a quick overview:

**For Organizers - Setting Up Judging:**

**Step 1: Add Judges**
• Go to the "Judges and Speakers" tab in hackathon setup
• Add judges, mentors, or speakers
• Choose judging mode (Main or Sponsor)
• Provide judge email addresses

📖 Guide: https://guide.devfolio.co/docs/guide/setting-up-your-hackathon/judges-tab

**Step 2: Set Judging Duration**
• Configure judging period at: https://org.devfolio.co/octant/judging

**Step 3: Allocate Projects**
• Assign projects to respective judges

� Complete Guide: https://guide.devfolio.co/docs/guide/organizer-judging

**For Judges - Getting Started:**

**Access Requirements:**
1. Create Devfolio account: https://devfolio.co/signup (mandatory)
2. Access judging portal: devfolio.co/judging/<your-hackathon-slug>
3. Check email for invitation link

📹 Demo Video: https://drive.google.com/file/d/1nDXh4K-F_VMFglr-afVc_xq08d1shdmM/view

**How It Works:**
1. Projects submitted by participants
2. Organizers assign projects to judges
3. Judges evaluate based on criteria
4. Scores calculated automatically
5. Winners announced

**Judging Modes:**
• **Online Judging** - Remote evaluation
• **Offline Judging** - In-person review
• **Quadratic Voting** - Community-based
• **Organizer Judging** - Direct review

💡 Judges should access via the email registered in "Speakers & Judges" tab
""",
    
    "submission": """
📤 **Project Submission**

**How to Submit:**
1. Go to your hackathon dashboard
2. Click "Submit Project"
3. Enter project details:
   • Title and tagline
   • Description
   • Tech stack used
   • Demo link/video
   • GitHub repository
4. Add team members if applicable
5. Click "Submit"

**Important:**
• Submit before the deadline
• You can edit until submission closes
• Include a working demo if possible
• Add clear documentation

**Pro Tips:**
✅ Test all links before submitting
✅ Add screenshots/video demos
✅ Explain what makes your project unique

Need help? Just ask me your specific question!
""",
    
    "team": """
👥 **Teams on Devfolio**

**Creating a Team:**
1. Go to hackathon page
2. Click "Create Team"
3. Set team name
4. Share invite code with members

**Joining a Team:**
1. Get invite code from team leader
2. Go to hackathon page
3. Click "Join Team"
4. Enter the invite code

**Team Rules:**
• Max team size varies by hackathon
• All members must be registered
• Only team leader submits project
• All members share the submission

**Managing Teams:**
• Team leader can remove members
• Members can leave anytime
• Changes allowed until submission

Questions? Just ask me!
""",
    
    "tracks": """
🏆 **Tracks & Prizes**

**Adding Tracks:**

**Step 1: Access Prizes Tab**
• Go to the "Prizes" tab on your Organizer Dashboard

**Step 2: Create Track**
• Click "Add Track" button (top-right)
• Enter Track Name
• Add clear Description
• Click "Add Track" to save

**Important Notes:**
• Only organizers can add/edit tracks
• You can add as many tracks as needed
• Tracks help guide participants toward specific themes
• Makes submissions easier to review and judge

💡 Tracks are a great way to organize prizes by category or sponsor!
""",
    
    "support": """
💬 **Get Additional Support**

**Need More Help?**

**For Hackathon-Specific Questions:**
• Ask organizers directly in their group/channel

**Documentation & Guides:**
🌐 Complete Guide: https://guide.devfolio.co/


**Response Time:**
• We typically respond within 24 hours or less

"""
}

