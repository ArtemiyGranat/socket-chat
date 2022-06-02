let is_file = false
let file_path

// Send functions

async function send_name() {
    username = document.getElementById("username_field").value
    if (username.trim().length >= 3 && username.length <= 12) {
        let answer = eel.connect(username.trim())
        if (answer == true) {
            document.getElementById('signin_btn').setAttribute('onclick','resend_username()')
        }
    }
    else {
        get_exception("Wrong username input, please, choose another one")
    }
}

function resend_username() {
    username = document.getElementById("username_field").value
    eel.resend_username(username)
}

async function send_message() {
    if (!is_file) {
        let text = document.getElementById("msgbox").value
        if (text.trim().length > 0 && text.trim().length <= 5000) {
            document.getElementById("msgbox").value = ""
            display_sent_msg(text)
            eel.send_message(text)
        }
        else {
            get_exception("Message must not be empty and its length must not exceed 5000 characters")
        }
    }
    else {
        eel.send_file(file_path)
        show_input()
    }
}

// Display functions

function display_recv_msg(usrname, text, is_file_recvd) {
    var div = document.createElement("div");
    div.className = "align-items-baseline mb-1";

    var second_div = document.createElement("div");
    second_div.className = "pe-2";
    div.appendChild(second_div);

    var third_div = document.createElement("div");
    third_div.className = "recv-msg-div card card-text p-2 px-3 m-1";
    second_div.appendChild(third_div);

    var usrname_div = document.createElement("div")
    usrname_div.className = "username"
    var usrname_text = document.createTextNode(usrname)
    usrname_div.appendChild(usrname_text)
    third_div.appendChild(usrname_div)

    var msg_div = document.createElement("div")
    var msg = document.createTextNode(text)
    msg_div.appendChild(msg)
    third_div.appendChild(msg_div)
    
    if (is_file_recvd) {
        var download_btn = document.createElement("button");
        download_btn.innerHTML = "Download";
        download_btn.className = "btn btn-primary"; // TODO: кастом кнопки
        download_btn.addEventListener("click", function() {
            eel.download_file(text)
        }, false);
        third_div.appendChild(download_btn)
    }

    var time_div = document.createElement("div")
    time_div.className = "time"
    var date = new Date().toLocaleTimeString('en-US', { hour12: false,
        hour: "numeric", 
        minute: "numeric"
    });
    var time_text = document.createTextNode(date)
    time_div.appendChild(time_text)
    third_div.appendChild(time_div)


    var chat_body = document.getElementById("chat-body");
    chat_body.appendChild(div)
    chat_body.scrollTo({
        top:chat_body.scrollHeight, 
        behavior:"smooth"
    })
}

function display_sent_msg(text) {
    var div = document.createElement("div");
    div.className = "align-items-baseline justify-content-end mb-1";

    var second_div = document.createElement("div");
    second_div.className = "pe-2";
    div.appendChild(second_div);

    var third_div = document.createElement("div");
    third_div.className = "sent-msg-div card card-text p-2 px-3 m-1";
    second_div.appendChild(third_div);

    var usrname_div = document.createElement("div")
    usrname_div.className = "you"
    var usrname_text = document.createTextNode("You")
    usrname_div.appendChild(usrname_text)
    third_div.appendChild(usrname_div)

    var msg_div = document.createElement("div")
    var msg = document.createTextNode(text)
    msg_div.appendChild(msg)
    third_div.appendChild(msg_div)

    var time_div = document.createElement("div")
    time_div.className = "time"
    var date = new Date().toLocaleTimeString('en-US', { hour12: false,
        hour: "numeric", 
        minute: "numeric"
    });
    var time_text = document.createTextNode(date)
    time_div.appendChild(time_text)
    third_div.appendChild(time_div)

    var chat_body = document.getElementById("chat-body");
    chat_body.appendChild(div)
    chat_body.scrollTo({
        top:chat_body.scrollHeight,
         behavior:"smooth"
        })
}

function show_input() {
    is_file = false
    document.getElementById("msgbox").readOnly = false;
    document.getElementById("msgbox").value = "";
}

// Eel exposed functions

eel.expose(open_chat);
function open_chat() {
    document.getElementById("log-in-screen").hidden = true;
    window.resizeTo(1200, 800);
    document.getElementById("chat-screen").hidden = false;
}

eel.expose(username_reentry);
function username_reentry() {
    alert("This username is already taken, please choose another one")
}

eel.expose(get_recv_msg);
function get_recv_msg(usrname, msg) {
    display_recv_msg(usrname, msg, false)
}

eel.expose(get_recv_file);
function get_recv_file(usrname, msg) {
    display_recv_msg(usrname, msg, true)
}

eel.expose(show_filename);
function show_filename(filepath) {
    is_file = true
    file_path = filepath
    document.getElementById("msgbox").readOnly = true;
    document.getElementById("msgbox").value = filepath;
}

eel.expose(close_window);
function close_window() {
    window.close()
}

eel.expose(get_exception);
function get_exception(ex) {
    // $('#exceptionModal').modal('show');
    alert(ex);
}

// Key pressed functions

function username_field_key_pressed(event) {
    if (event.keyCode == 13) {
        send_name()
        // document.getElementById('username_field').setAttribute('onkeydown','()')
    }
}

function messagebox_field_key_pressed(event) {
    if (event.keyCode == 13) {
        send_message()
    }
}

// File functions
function open_file() {
    eel.open_file();
}