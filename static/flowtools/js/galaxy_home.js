if (!Function.prototype.bind) {
    Function.prototype.bind = function (oThis) {
        if (typeof this !== "function") {
            // closest thing possible to the ECMAScript 5 internal IsCallable function
            throw new TypeError("Function.prototype.bind - what is trying to be bound is not callable");
        }
        var aArgs = Array.prototype.slice.call(arguments, 1), 
            fToBind = this, 
            fNOP = function () {},
            fBound = function () {
              return fToBind.apply(this instanceof fNOP && oThis
                ? this : oThis, aArgs.concat(Array.prototype.slice.call(arguments)));
            };
        fNOP.prototype = this.prototype;
        fBound.prototype = new fNOP();
        return fBound;
    };
}

function replaceContextRoot(input, contextRoot) {
	if (typeof(input) == 'undefined') {
		return "";
	}
	contextRoot = CONTEXT_ROOT || CONTEXT_ROOT;
	var result = input.replace('CONTEXT_ROOT', contextRoot);
	return result
}

function parseTsvData(data) {
	var items = [];
	var lines = data.split('\n');
	var headers = lines[0].split('\t');
	for (var i = 1; i < lines.length; i++) {
		  var content = lines[i].split('\t');
		  var item = {};
		  for (var count = 0; count < headers.length; count++) {
			  item[headers[count]] = replaceContextRoot(content[count]);
		  }
		  items.push(item);
	}
	return items;
}


function updateAnnouncements() {
	var items = [];
	var slidesDataUrl = '/static/data/announcements.txt';
	$.get(slidesDataUrl, function(data) {
		var items = parseTsvData(data);
        displayAnnouncements(items);
	});
}

function displayAnnouncements(items) {
	var announcementBody = $('.right-info-panels .panel-body');
	for (var i = 0; i < items.length; i++) {
		var item = items[i];
		var announcementInfoSource = $("#announcement-info-template").html();
		var announcementItemHtml = Handlebars.compile(announcementInfoSource)(item);
		announcementBody.append(announcementItemHtml);
	}
}

function onAnnouncementClick(event) {
	var targetElement = $(event.target);
	var announcement = {
		type: targetElement.attr('data-type'),
		link: targetElement.attr('data-link'),
		display: targetElement.attr('data-display')
	}
	switch (announcement.display) {
	case 'popup':
		window.open(announcement.link, '_blank');
		break;
	case 'internal':
		// internal link
		window.open(announcement.link, '_blank');
		break;
	case 'external':
		// external link
		window.open(announcement.link, '_blank');
		break;
	}
}

function updateCarousel() {
	var items = [];
	var slidesDataUrl = '/static/data/slides.txt';
	$.get(slidesDataUrl, function(data) {
		var items = parseTsvData(data);
        setupCarousel(items);
        if (items[0] && items[0].title) {
        	$('.carousel-top-title').html(items[0].title);
        }
	});
}

function updateCarouselTitle(slide) {
	var slideTitle = $(slide).find('.carousel-item-title').html();
	$('.carousel-top-title').html(slideTitle);
}

function setupCarousel(items) {
	var carouselIndicator = $('#carousel-immport-share .carousel-indicators');
	var carouselBody = $('#carousel-immport-share .carousel-inner');
	// add carousel items
    for (var i = 0; i < items.length - 1; i++) {
    	var item = items[i];
    	item.itemIndex = i;
    	item.itemActiveText = (i === 0) ? 'active' : '';
    	item.itemTarget = '#carousel-immport-share';
    	
    	// carousel item indicator 
    	var carouselIndicatorSource = $("#carousel-indicator-template").html();
    	var carouselIndicatorHtml = Handlebars.compile(carouselIndicatorSource)(item);
    	carouselIndicator.append(carouselIndicatorHtml);

    	// carousel item body
    	var carouselItemSource = $("#carousel-item-template").html();
     	var carouselItemHtml = Handlebars.compile(carouselItemSource)(item);
    	carouselBody.append(carouselItemHtml);

    }
}

