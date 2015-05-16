$( document ).ready(function() {
    $.getJSON('/intl-city-list', function(result) {

    	$('#typeahead-city1').typeahead({
	    	source: {
	    		data: result.cities
	    	}	    
		});

    	$('#typeahead-city2').typeahead({
	    	source: {
	    		data: result.cities
	    	}	    
		});

    });

    $.getJSON('/us-city-list', function(result) {
    	$('#typeahead-departure-city').typeahead({
	    	source: {
	    		data: result.us_cities
	    	}	    
		});

    });
    
});