MAX_LINK_DURATION = 120;

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
    ajaxPost(
        {target: target},
        '/api/link-add/',
        addLinkResponse
    );

    function addLinkResponse(response) {
        var add_link = $('.add-link');
        if (response.result === 0) {
            var url = build_url(response.path);
            $('.link-url').html(url);
            $('button.add-another').show();
        }
        else { // there's an error
            var error = $('form.main .error');
            add_link.prop('disabled', false);
            add_link.select();
            if (response.error === "ValidationError") {
                error.text('Whoops, that\'s not a valid URL!')
            }
            else if (response.error === "AccessError") {
                error.text('You are limited to 10 active links at a time. Log in or create an account to double this limit.')
            }
            else if (response.error === "CapacityError") {
                error.text('Uh oh! kikl.co is currently at capacity. An administrator has been notified; check back in a bit to try again. Sorry for the inconvenience!')
            }
            else {
                error.text('An unexpected error occured. Sorry I couldn\'t be more specific. Maybe check your internet connection? If that\'s alright, the fact that you\'re seeing this means we screwed up!');
            }
        }
    }
}

function ajaxIncreaseDuration(link) {
    link_id = link.attr('data-id');
    ajaxPost(
        {link: link_id},
        '/api/link-increaseduration/',
        increaseDurationResponse
    );

    function increaseDurationResponse(response) {
        if (response.result === 0) {
            var total = response.new_duration;
            var secs_remaining = response.new_secs_remaining;
            link.attr('data-total', total);
            link.attr('data-remaining', secs_remaining);

            if (total >= MAX_LINK_DURATION) {
                link.find('button.add-time').hide();
            }
        }
        else console.log(response);
    }
}

function build_url(path) {
    var prefix = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '')+'/'
    var path = '<span class="path">'+path+'</span>';
    var url = prefix + path;
    return url;
}

function format_time(secs) {
    var minutes = Math.floor(secs/60);
    var seconds = secs - minutes*60;
    return {total: secs, minutes: minutes, seconds: seconds};
}

function timer(link) { // http://stackoverflow.com/a/5927432
    var time = link.find('.timer');
    var progress_bar = link.find('.progress-bar');
    var before = new Date();
    var interval = 1000;
    this.interval_id = setInterval(function(){
        var remaining = parseInt(link.attr('data-remaining'));
        var total = parseInt(link.attr('data-total')) * 60;
        set_progress_bar(progress_bar, remaining, total);
        if (remaining <= 0) {
            clearInterval(this.interval_id);
            time.text('0:00');
            link.find('button.add-time').unbind('click').addClass('disabled');
            return;
        }
        var now = new Date();
        var elapsed_time = now.getTime() - before.getTime();
        if (elapsed_time > interval) 
            link.attr('data-remaining', remaining - Math.floor(elapsed_time/interval));
        else
            link.attr('data-remaining', remaining - 1);
        var ft = format_time(remaining);
        time.text(ft.minutes+':'+pad(ft.seconds));
        before = new Date();
    }, interval);
}

function set_progress_bar(elem, remaining, total) {
    var percent = (remaining/total) * 100;
    elem.css('width', percent+'%');
}


/* utility functions */

function pad(n) { // http://stackoverflow.com/a/2998822
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
