$( document ).ready(function() {

   
});

		$("#typeahead-departure-city").on("change", function(evt) {
    	if ($.inArray($("#typeahead-departure-city").val(), result.us_cities) === -1) 
    		{alert("Please choose a destination from the dropdown.")}
    });