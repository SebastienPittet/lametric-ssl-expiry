// bulma tab switching and display related content
$(function() {
    const tabs = document.querySelectorAll('.tabs li');
    const tabContentBoxes = document.querySelectorAll('#tab-content > div');
    
    tabs.forEach((tab) => {
        tab.addEventListener('click', () => {
            tabs.forEach(item => item.classList.remove('is-active'))
            tab.classList.add('is-active');
    
            const target = tab.getAttribute('id');

            tabContentBoxes.forEach(box => {
                if(box.getAttribute('id') === target) {
                    box.classList.remove('is-hidden');                
                } else {
                    box.classList.add('is-hidden');
                }
            })
        })
    })
})

// get form values, submit the form and display the results
$(function() {
    $(".button").click(function() {
        const expiry_url = "/api";

        var formData = {
            hostname: $("#hostname").val(),
            port: $("#port").val()
        }
        
        var settings = {
            'cache': false,
            'dataType': 'json',
            'data' : formData,
            'async': true,
            'crossDomain': true,
            'method': 'GET',
            'headers': {
                'accept': 'application/json',
            }
        }

        // ask the backend and init the page
        $.ajax(expiry_url, settings).done(function (response) {
            var expiry = $("#hostname").val() + " will expire in " + response['frames'][1]['text'] + ".";

            // set the value and show results
            $("#expiryTime").text(expiry);
            $("#answer").removeClass("is-hidden");
        })
    }
)});

// click on delete button from the answer and remove it
$(function() {
    $(".delete").click(function() {
        $("#answer").addClass("is-hidden");
    }
)});
