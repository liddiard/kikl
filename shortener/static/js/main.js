$(document).ready(function() {
    var add_link = $('.add-link');
    add_link.on('input', function(){ addLinkInputChange(add_link) });
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
            // add_link.prop('disabled', false);
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
                error.text('Uh oh! kikl.co is currently at capacity. We\'re really sorry about that; an administrator has been notified of the problem. Check back later and try again.')
            }
            else {
                error.text('An unexpected error occured. Sorry I couldn\'t be more specific. Maybe check your internet connection? If that\'s alright, the fact that you\'re seeing this means we screwed up!');
            }
        }
    }
}


/* utility functions */

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
