// Check if jQuery is defined
if (typeof jQuery === 'undefined') {
    // If not defined, create a script element and load jQuery dynamically
    var script = document.createElement('script');
    script.src = 'https://code.jquery.com/jquery-3.6.0.min.js'; // Replace with the version you need
    script.onload = function () {
        // Now jQuery is loaded, you can use it
        main(); // Call your main function or perform other tasks
    };
    document.head.appendChild(script);
} else {
    // jQuery is already defined, you can use it directly
    main(); // Call your main function or perform other tasks
}

function main() {
    // Your main code that uses jQuery
    $(document).ready(function () {
        var scriptTag = $('script[src*="fair-review-output.js"]');

        // Extract the query string from the src attribute
        var queryString = scriptTag.attr('src').split('?')[1];

        // Parse the query string into key-value pairs
        var queryParams = {};
        queryString.split('&').forEach(function (param) {
            var keyValue = param.split('=');
            queryParams[keyValue[0]] = keyValue[1];
        });

        // Access the apiKey
        var apiKey = queryParams.apiKey;

        // Now you can use the apiKey in your script
        if(apiKey != ""){
            $('.product-review-wrapper').each(function(i, elm){                
                let puid = $(elm).attr('fr-pdt-uuid');
                if(puid != "" && puid !== 'undefined'){
                    let data = {                        
                        'puid': puid
                    }

                    $.ajax({
                        url: "http://127.0.0.1:5000/api/v1/review/",
                        method: "GET",
                        data: data,
                        headers: {
                            'X-API-Key': apiKey                            
                        },
                        success: function(data){
                            console.log('success');
                            let response = data;
                            $(elm).html(response);
                        },
                        error: function(xhr, status, err){
                            console.log(xhr);
                        }
                    })                    
                }
            })
        }
    });
}