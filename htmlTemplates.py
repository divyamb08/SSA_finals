css = '''
<style>
body {
    font-family: Arial, sans-serif;
    background: linear-gradient(90deg, #ffffff 0%, #ffffff 50%, #f2f2f2 50%, #f2f2f2 100%);
}
.chat-message {
    padding: 1.5rem;
    border-radius: 0.5rem;
    margin-bottom: 1rem;
    display: flex;
}
.chat-message.user {
    background-color: #ffffff;
    color: #000;
}
.chat-message.bot {
    background-color: #f2f2f2;
    color: #000;
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
    color: #000;
}
'''

bot_template = '''
<div class="chat-message bot">
    <div class="avatar">
        <img src="https://final-project-spicestack.s3.us-east-2.amazonaws.com/proj_logo.png">
    </div>
    <div class="message">{{MSG}}</div>
</div>
'''

user_template = '''
<div class="chat-message user">
    <div class="avatar">
        <img src="data:image/png;base64,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">
    </div>    
    <div class="message">{{MSG}}</div>
</div>
'''
