import 'mdui/mdui.css';
import './app.css';
import { loadLocale } from 'mdui/functions/loadLocale.js';
import { setLocale } from 'mdui/functions/setLocale.js';
import { getLocale } from 'mdui/functions/getLocale.js';
import 'mdui/components/avatar.js';
import 'mdui/components/text-field.js';
import 'mdui/components/button.js';
import { $ } from 'mdui/jq.js';
import { alert } from 'mdui/functions/alert.js';

const BaseHost = 'http://127.0.0.1:8000'

loadLocale(() => import(`../node_modules/mdui/locales/zh-cn.js`));

setLocale('zh-cn').then(() => {
    console.log(getLocale()); // zh-cn
});

function get_username() {
    return $('#username').val().trim();
}

function get_password() {
    return $('#password').val();
}

function get_email() {
    return $('#email').val().trim();
}

function get_captcha_text() {
    return $('#captcha-code').val();
}

async function get_captcha(session_id) {
    const promise = $.ajax({
        method: 'POST',
        url: `${BaseHost}/captcha/`,
        data: JSON.stringify({
            "session_id": session_id
        }),
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        statusCode: {
            200: function (data, textStatus, xhr) {
                $('#captcha').empty();
                $('#captcha').append('<img src=' + data.b64 + ' />');
            },
            404: function (xhr, textStatus) {
                get_session_id();
            },
            422: function (xhr, textStatus) {
                console.log(textStatus);
                console.log(xhr);
            }
        }
    })
}

async function get_session_id() {
    const promise = $.ajax({
        method: 'GET',
        url: `${BaseHost}/captcha/session`,
        statusCode: {
            200: function (data, textStatus, xhr) {
                localStorage.setItem("session_id", data.session_id);
                get_captcha(data.session_id);
            },
            422: function (xhr, textStatus) {
                console.log(textStatus);
            }
        }
    })
}


async function initialize() {
    if (session_id == null) {
        get_session_id();
    } else {
        console.log(session_id.toString());
        get_captcha(session_id);
    }
}

let session_id = localStorage.getItem("session_id");

initialize();

let usernameField = false, passwordField = false, emailField = false, captchaFiled = false;

$('#btn1').attr('disabled', true);

$('#captcha').on('click', async function () {
    session_id = localStorage.getItem("session_id");
    get_captcha(session_id);
})

$('#username').on('blur', async function () {
    const _username = get_username();
    const _username_helper = $('#username-helper');
    if (_username !== "") {
        $.ajax({
            method: "POST",
            url: `${BaseHost}/verify/username`,
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({
                "username": _username
            }),
            statusCode: {
                200: function (data, textStatus, xhr) {
                    if (data.exist == true) {
                        _username_helper.attr('style', 'color: red');
                        _username_helper.text("用户名已被注册");
                        usernameField = false;
                    } else {
                        _username_helper.attr('style', 'color: green');
                        _username_helper.text("该用户名可用(๑´ㅂ`๑)");
                        usernameField = true;
                    }
                },
                422: function (xhr, textStatus) {
                    console.log(textStatus, xhr);
                    usernameField = false;
                }
            }
        })
    } else {
        _username_helper.attr('style', 'color: red');
        _username_helper.text("用户名不能为空嗷~");
        usernameField = false;
    }
})

$('#email').on('blur', async function () {
    const _email = get_email();
    const _email_helper = $('#email-helper');
    if (_email !== "") {
        const emailRegex = /@csuwf\.com$/;
        if (!emailRegex.test(_email)) {
            _email_helper.attr('style', 'color: red');
            _email_helper.text("邮箱必须以@csuwf.com结尾");
            emailField = false;
        } else {
            $.ajax({
                method: "POST",
                url: `${BaseHost}/verify/email`,
                dataType: "json",
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({
                    "email": _email
                }),
                statusCode: {
                    200: function (data, textStatus, xhr) {
                        if (data.exist == true) {
                            _email_helper.attr('style', 'color: red');
                            _email_helper.text("该邮箱不可使用 ")
                            emailField = false;
                        } else {
                            _email_helper.attr('style', 'color: green');
                            _email_helper.text("该邮箱可用")
                            emailField = true;
                        }
                    },
                    422: function (xhr, textStatus) {
                        console.log(textStatus, xhr);
                    }
                }
            })
        }
    } else {
        _email_helper.attr('style', 'color: blue');
        _email_helper.text("快选一个网服专属邮箱吧~");
        emailField = false;
    }
})

$('#password').on("blur", async function () {
    const _password = get_password();
    const _password_helper = $('#password-helper');
    if (_password !== "") {
        const passwordRegex = /[&\\;!#$^*()'"]/;
        if (passwordRegex.test(_password)) {
            _password_helper.attr('style', 'color: #4269f5');
            _password_helper.text("检测到密码包含特殊字符，注册后记得阅读手册的注意事项");
            passwordField = true;
        } else if (_password.length <= 6) {
            _password_helper.attr('style', 'color: red');
            _password_helper.text("密码长度必须大于6位");
            passwordField = false;
        }
        else {
            _password_helper.attr('style', 'color: green');
            _password_helper.text("ok~");
            passwordField = true;
        }
    }
    else {
        _password_helper.attr('style', 'color: red');
        _password_helper.text("密码不能为空");
        passwordField = false;
    }
})

$('#captcha-code').on('blur', async function () {
    const captcha_text = get_captcha_text();
    const captcha_helper = $('#captcha-helper');
    if (captcha_text.length != 4) {
        captcha_helper.attr('style', 'color: red');
        captcha_helper.text("验证码长度不正确噢~");
        captchaFiled = false;
    } else {
        const session_id = localStorage.getItem("session_id");
        $.ajax({
            method: "POST",
            url: `${BaseHost}/verify/captcha`,
            data: JSON.stringify({
                "code": captcha_text,
                "session_id": session_id
            }),
            dataType: "json",
            contentType: "application/json; charset=utf-8",
            statusCode: {
                200: function (data, textStatus, xhr) {
                    if (data.ok === true) {
                        captcha_helper.attr('style', 'color: green');
                        captcha_helper.text("验证码正确");
                        captchaFiled = true;
                    } else {
                        captcha_helper.attr('style', 'color: red');
                        if (data.reason === "invalid") {
                            captcha_helper.text("验证码错误");
                        } else if (data.reason == "timeout") {
                            captcha_helper.text("验证码无效，请重新输入");
                            get_captcha(session_id);
                        }
                        captchaFiled = false;
                    }
                },
                404: function(xhr, textStatus) {
                    captchaFiled = false;
                },
                422: function (xhr, textStatus) {
                    captchaFiled = false;
                    console.log(xhr);
                }
            }
        })
    }
})

function setButtonStatus() {
    if (usernameField && passwordField && emailField && captchaFiled) {
        $('#btn1').attr('disabled', false);
    } else {
        $('#btn1').attr('disabled', true);
    }
}

const intervalTask = setInterval(setButtonStatus, 1000);


$('#btn1').on('click', async function () {
    const btn1 = $('#btn1');
    const _username = get_username();
    const _password = get_password();
    const _email = get_email();
    const _captcha_text = get_captcha_text();
    const _session_id = localStorage.getItem("session_id");
    console.log(_username, _password, _email, _captcha_text);
    clearInterval(intervalTask);
    btn1.attr('loading', true);
    btn1.attr('disabled', true);
    $.ajax({
        method: "POST",
        url: `${BaseHost}/user/register`,
        dataType: "json",
        contentType: "application/json; charset=utf-8",
        data: JSON.stringify({
            "username": _username,
            "password": _password,
            "email": _email,
            "session_id": _session_id,
            "code": _captcha_text
        }),
        statusCode: {
            200: function (data, textStatus, xhr) {
                if (data.ok === true) {
                    alert({
                        headline: "注册结果",
                        description: `成功，您的用户名: ${_username} 密码: ${_password} 邮箱: ${_email} `,
                        onConfirm: () => {
                            btn1.removeAttr("loading");
                            btn1.removeAttr("disabled");
                        }
                    })
                } else {
                    alert({
                        headline: "注册结果",
                        description: "失败，" + data.reason,
                        confirmText: "了解",
                        onConfirm: () => {
                            btn1.removeAttr("loading");
                            btn1.removeAttr("disabled");
                        }
                    })
                }
            },
            404: function(xhr, textStatus) {
                alert({
                    headline: "注册结果",
                    description: "失败，" + textStatus,
                    confirmText: "了解",
                    onConfirm: () => {
                        btn1.removeAttr("loading");
                        btn1.removeAttr("disabled");
                    }
                })
            },
            422: function (xhr, textStatus) {
                alert({
                    headline: "注册结果",
                    description: "失败，" + textStatus,
                    confirmText: "了解",
                    onConfirm: () => {
                        btn1.removeAttr("loading");
                        btn1.removeAttr("disabled");
                    }
                })
            }
        }
    })
})