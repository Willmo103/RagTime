css = """
<style>
.chat-message {
    padding: 1.5rem; border-radius: 0.5rem; margin-bottom: 1rem; display: flex
}
.chat-message.user {
    background-color: #2b313e
}
.chat-message.bot {
    background-color: #475063
}
.chat-message .avatar {
  width: 20%;
}
.chat-message .avatar img {
  max-width: 78px;
  max-height: 78px;
  border-radius: 50%;
  object-fit: cover;
}
.chat-message .message {
  width: 80%;
  padding: 0 1.5rem;
  color: #fff;
}
.scrollable-chat-area {
    overflow-y: auto;
    max-height: 60vh; /* Adjust based on your needs */
    margin-bottom: 20px; /* Space above the fixed input */
}

.fixed-input {
    position: fixed;
    bottom: 0;
    left: 0;
    width: 100%;
    padding: 10px 50px; /* Adjust padding as needed */
    box-shadow: 0px -4px 6px -1px rgba(0,0,0,0.1);
    z-index: 1;
}

"""

bot_template = """
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://i.ibb.co/cN0nmSj/Screenshot-2023-05-28-at-02-37-21.png" style="max-height: 78px; max-width: 78px; border-radius: 50%; object-fit: cover;">
    </div>
    <div class="message">{{MSG}}</div>
</div>
"""

user_template = """
<div class="chat-message user">
    <div class="avatar">
        <img src="src\\static\\img\\_e7d34fcf-3cd8-45fd-bd47-d4ac850de492.jpg">
    </div>
    <div class="message">{{MSG}}</div>
</div>
"""
