$( document ).ready(function() {
    $.getJSON('/city-list', function(result) {

    	$('.typeahead').typeahead({
	    	source: {
	    		data: result.cities
	    	}	    
		});
    });
    
});