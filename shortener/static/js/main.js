$(document).ready(function() {
    var add_link = $('.add-link');
    add_link.on('input', function(){ addLinkInputChange(add_link) });
    $('button.add-another').click(function(){
        add_link.prop('disabled', false).val('').focus();
        $(this).hide();
    });
});

function addLinkInputChange(elem) {
    var target = elem.val();
    if (target.length > 0) {
        console.log("detected a non-zero input change");
        elem.prop('disabled', true);
        ajaxAddLink(target);
    } else elem.prop('disabled', false);
}

function ajaxAddLink(target) {
    console.log(target);
    ajaxPost(
        {target: target},
        '/api/link-add/',
        addLinkResponse
    );

    function addLinkResponse(response) {
        var add_link = $('.add-link');
        if (response.result === 0) {
            var url = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '')+'/'+response.path;
            $('.link').text(url);
            $('button.add-another').show();
        }
        else { // there's an error
            var error = $('form.main .error');
            add_link.prop('disabled', false);
            add_link.select();
            if (response.error === "ValidationError") {
                error.text('That\'s not a valid url!')
            }
            else if (response.error === "AccessError") {
                error.text('You are limited to 10 active links at a time. Log in or create an account to double this limit.')
            }
            else if (response.error === "CapacityError") {
                error.text('Uh oh! kikl.co is currently at capacity. We\'re really sorry about that; an administrator has been notified of the problem. Check back later to try again.')
            }
            else {
                error.text('An unexpected error occured. Sorry I couldn\'t be more specific. Maybe check your internet connection? If that\'s alright, the fact that you\'re seeing this means we screwed up!');
            }
        }
    }
}

function format_time(secs) {
    var minutes = Math.floor(secs/60);
    var seconds = secs - minutes*60;
    return {total: secs, minutes: minutes, seconds: seconds};
}

function timer(elem, remaining, total) {
    // http://stackoverflow.com/a/5927432
    var before = new Date();
    var interval = 1000;
    this.interval_id = setInterval(function(){
        if (remaining <= 0) {
            clearInterval(this.interval_id);
            elem.text('0:00');
            return;
        }
        var now = new Date();
        var elapsed_time = now.getTime() - before.getTime();
        if (elapsed_time > interval) 
            remaining -= Math.floor(elapsed_time/interval);
        else
            remaining--;
        var ft = format_time(remaining);
        elem.text(ft.minutes+':'+pad(ft.seconds));
        set_progress_bar($('.progress-bar'), remaining, total);
        before = new Date();
    }, interval);
}

function set_progress_bar(elem, remaining, total) {
    var percent = (remaining/total) * 100;
    elem.css('width', percent+'%');
}


/* utility functions */

function pad(n) {
    // http://stackoverflow.com/a/2998822
    return (n < 10) ? ("0" + n) : n;
}

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

function ajaxPost(params, endpoint, callback_success) {
    params.csrfmiddlewaretoken = getCookie('csrftoken');
    $.ajax({
        type: "POST",
        url: endpoint,
        data: params,
        success: callback_success,
        error: function(xhr, textStatus, errorThrown) {
            console.log("Oh no! Something went wrong. Please report this error: \n"+errorThrown+xhr.status+xhr.responseText);
        }
    }); 
}
