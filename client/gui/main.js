// Send functions

function send_name() {
    username = document.getElementById("username_field").value
    eel.connect(username)
    document.getElementById('signin_btn').setAttribute('onclick','resend_username()')
}

function resend_username() {
    username = document.getElementById("username_field").value
    eel.resend_username(username)
}

async function send_message() {
    let text = document.getElementById("msgbox").value
    if (text != "") {
        document.getElementById("msgbox").value = ""
        display_sent_msg(text)
        eel.send_message(text)
    }
}

// Display functions

function display_recv_msg(usrname, text) {
    var div = document.createElement("div");
    div.className = "recv-msg-div row mx-3 mb-1"

    var usrname_div = document.createElement("div")
    usrname_div.className = "username"
    var usrname_text = document.createTextNode(usrname)
    usrname_div.appendChild(usrname_text)
    div.appendChild(usrname_div)

    var msg_div = document.createElement("div")
    msg_div.className = "recv-msg"
    div.appendChild(msg_div)

    var msg = document.createTextNode(text)
    msg_div.appendChild(msg)

    var time_div = document.createElement("div")
    time_div.className = "time"
    msg_div.appendChild(time_div)
    var date = new Date().toLocaleTimeString('en-US', { hour12: false,
                                                        hour: "numeric", 
                                                        minute: "numeric"
    });
    var time_text = document.createTextNode(date)
    time_div.appendChild(time_text)

    var messagebox_field = document.getElementById("input-msg-div")
    document.getElementById("rightside").insertBefore(div, messagebox_field)
    window.scrollTo(0, document.body.scrollHeight)
}

function display_sent_msg(text) {
    var div = document.createElement("div");
    div.className = "sent-msg-div row mx-3 mb-1"

    var usrname_div = document.createElement("div")
    usrname_div.className = "you"
    var usrname_text = document.createTextNode("You")
    usrname_div.appendChild(usrname_text)
    div.appendChild(usrname_div)

    var msg_div = document.createElement("div")
    msg_div.className = "sent-msg"
    div.appendChild(msg_div)

    var msg = document.createTextNode(text)
    msg_div.appendChild(msg)

    var time_div = document.createElement("div")
    time_div.className = "time"
    msg_div.appendChild(time_div)
    var date = new Date().toLocaleTimeString('en-US', { hour12: false,
                                                        hour: "numeric", 
                                                        minute: "numeric"
      });
    var time_text = document.createTextNode(date)
    time_div.appendChild(time_text)

    var messagebox_field = document.getElementById("input-msg-div")
    document.getElementById("rightside").insertBefore(div, messagebox_field)
    window.scrollTo(0, document.body.scrollHeight)
}

// Eel exposed functions

eel.expose(username_reentry);
function username_reentry() {
    alert("This username is already taken, please choose another one")
}

eel.expose(get_recv_msg);
function get_recv_msg(usrname, msg) {
    display_recv_msg(usrname, msg)
}

eel.expose(close_window);
function close_window() {
    window.close()
}

eel.expose(get_exception);
function get_exception(ex) {
    $('#exceptionModal').modal('show');
    // alert(ex);
}

// Key pressed functions

function username_field_key_pressed(event) {
    if (event.keyCode == 13) {
        send_name()
    }
}

function messagebox_field_key_pressed(event) {
    if (event.keyCode == 13) {
        send_message()
    }
}