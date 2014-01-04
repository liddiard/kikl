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
        if (response.result === 0) {
            var url = location.protocol+'//'+location.hostname+(location.port ? ':'+location.port: '')+'/'+response.path;
            $('.link').text(url);
        }
        else { // there's an error
            var add_link = $('.add-link');
            add_link.prop('disabled', false);
            add_link.select();
            if (response.error === "ValidationError") {
                console.log(response);
            }
            else if (response.error === "AccessError") {
                console.log(response);
            }
            else if (response.error === "CapacityError") {
                console.log(response);
            }
            else {
                console.log(response);
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
