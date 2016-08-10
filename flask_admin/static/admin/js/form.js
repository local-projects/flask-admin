var AdminForm = function() {
    // Field converters
    var fieldConverters = [];

    // Mapping of data-role keys to style callbacks
    this.fieldStyles = Object();

    this.fieldStyles['select2'] = function($el, name) {
        var opts = {
            width: 'resolve'
        };

        if ($el.attr('data-allow-blank'))
            opts['allowClear'] = true;

        if ($el.attr('data-tags')) {
            $.extend(opts, {
                tokenSeparators: [','],
                tags: []
            });
        }

        $el.select2(opts);
    };

    this.fieldStyles['select2-tags'] = function($el, name) {
        // get tags from element
        if ($el.attr('data-tags')) {
            var tags = JSON.parse($el.attr('data-tags'));
        } else {
            var tags = [];
        }

        // default to a comma for separating list items
        // allows using spaces as a token separator
        if ($el.attr('data-token-separators')) {
            var tokenSeparators = JSON.parse($el.attr('data-tags'));
        } else {
            var tokenSeparators = [','];
        }

        var opts = {
            width: 'resolve',
            tags: tags,
            tokenSeparators: tokenSeparators,
            formatNoMatches: function() {
                return 'Enter comma separated values';
            }
        };

        $el.select2(opts);

        // submit on ENTER
        $el.parent().find('input.select2-input').on('keyup', function(e) {
            if(e.keyCode === 13)
                $(this).closest('form').submit();
        });
    };

    this.fieldStyles['select2-ajax'] = function($el, name) {
        var multiple = $el.attr('data-multiple') == '1';

        var opts = {
            width: 'resolve',
            minimumInputLength: 1,
            placeholder: 'data-placeholder',
            ajax: {
                url: $el.attr('data-url'),
                data: function(term, page) {
                    return {
                        query: term,
                        offset: (page - 1) * 10,
                        limit: 10
                    };
                },
                results: function(data, page) {
                    var results = [];

                    for (var k in data) {
                        var v = data[k];

                        results.push({id: v[0], text: v[1]});
                    }

                    return {
                        results: results,
                        more: results.length == 10
                    };
                }
            },
            initSelection: function(element, callback) {
                $el = $(element);
                var value = jQuery.parseJSON($el.attr('data-json'));
                var result = null;

                if (value) {
                    if (multiple) {
                        result = [];

                        for (var k in value) {
                            var v = value[k];
                            result.push({id: v[0], text: v[1]});
                        }

                        callback(result);
                    } else {
                        result = {id: value[0], text: value[1]};
                    }
                }

                callback(result);
            }
        };

        if ($el.attr('data-allow-blank'))
            opts['allowClear'] = true;

        opts['multiple'] = multiple;

        $el.select2(opts);
    };

    this.fieldStyles['datepicker'] = function($el, name) {
        $el.daterangepicker({
            timePicker: false,
            showDropdowns: true,
            singleDatePicker: true,
            format: $el.attr('data-date-format')
        }, function(start, end) {
            $('.filter-val').trigger("change");
        });
    };

    this.fieldStyles['daterangepicker'] = function($el, name) {
        $el.daterangepicker({
            timePicker: false,
            showDropdowns: true,
            separator: ' to ',
            format: $el.attr('data-date-format')
        }, function(start, end) {
            $('.filter-val').trigger("change");
        });
    };

    this.fieldStyles['datetimepicker'] = function($el, name) {
        $el.daterangepicker({
            timePicker: true,
            showDropdowns: true,
            singleDatePicker: true,
            timePickerIncrement: 1,
            timePicker12Hour: false,
            format: $el.attr('data-date-format')
        }, function(start, end) {
            $('.filter-val').trigger("change");
        });

        $el.on('show.daterangepicker', function (event, data) {
            if ($el.val() == "") {
                var now = moment().seconds(0); // set seconds to 0
                // change datetime to current time if field is blank
                $el.data('daterangepicker').setCustomDates(now, now);
            }
        });
    };

    this.fieldStyles['datetimerangepicker'] = function($el, name) {
        $el.daterangepicker({
            timePicker: true,
            showDropdowns: true,
            timePickerIncrement: 1,
            timePicker12Hour: false,
            separator: ' to ',
            format: $el.attr('data-date-format')
        }, function(start, end) {
            $('.filter-val').trigger("change");
        });
    };

    this.fieldStyles['timepicker'] = function($el, name) {
        $el.daterangepicker({
            // Bootstrap 2 option
            timePicker: true,
            showDropdowns: true,
            format: $el.attr('data-date-format'),
            timePicker12Hour: false,
            timePickerIncrement: 1,
            singleDatePicker: true
        }, function(start, end) {
            $('.filter-val').trigger("change");
        });
        // hack to hide calendar to create a time-only picker
        $el.data('daterangepicker').container.find('.calendar-date').hide();
        $el.on('showCalendar.daterangepicker', function (event, data) {
            var $container = data.container;
            $container.find('.calendar-date').remove();
        });
    };

    this.fieldStyles['timerangepicker'] = function($el, name) {
        $el.daterangepicker({
            // Bootstrap 2 option
            timePicker: true,
            showDropdowns: true,
            format: $el.attr('data-date-format'),
            timePicker12Hour: false,
            separator: ' to ',
            timePickerIncrement: 1
        }, function(start, end) {
            $('.filter-val').trigger("change");
        });
        // hack - hide calendar + range inputs
        $el.data('daterangepicker').container.find('.calendar-date').hide();
        $el.data('daterangepicker').container.find('.daterangepicker_start_input').hide();
        $el.data('daterangepicker').container.find('.daterangepicker_end_input').hide();
        // hack - add TO between time inputs
        $el.data('daterangepicker').container.find('.left').before($('<div style="float: right; margin-top: 20px; padding-left: 5px; padding-right: 5px;"> to </span>'));
        $el.on('showCalendar.daterangepicker', function (event, data) {
            var $container = data.container;
            $container.find('.calendar-date').remove();
        });
    };

    this.fieldStyles['leaflet'] = function($el, name) {
        if (!window.MAPBOX_MAP_ID) {
            console.error("You must set MAPBOX_MAP_ID in your Flask settings to use the map widget");
            return false;
        }

        var geometryType = $el.data("geometry-type");
        if (geometryType) {
            geometryType = geometryType.toUpperCase();
        } else {
            geometryType = "GEOMETRY";
        }
        var multiple = geometryType.lastIndexOf("MULTI", geometryType) === 0;
        var editable = ! $el.is(":disabled");

        var $map = $("<div>").width($el.data("width")).height($el.data("height"));
        $el.after($map).hide();

        var center = null;
        if($el.data("lat") && $el.data("lng")) {
            center = L.latLng($el.data("lat"), $el.data("lng"));
        }

        var maxBounds = null;
        if ($el.data("max-bounds-sw-lat") && $el.data("max-bounds-sw-lng") &&
            $el.data("max-bounds-ne-lat") && $el.data("max-bounds-ne-lng"))
        {
            maxBounds = L.latLngBounds(
                L.latLng($el.data("max-bounds-sw-lat"), $el.data("max-bounds-sw-lng")),
                L.latLng($el.data("max-bounds-ne-lat"), $el.data("max-bounds-ne-lng"))
            );
        }

        var editableLayers;
        if ($el.val()) {
            editableLayers = new L.geoJson(JSON.parse($el.val()));
            center = center || editableLayers.getBounds().getCenter();
        } else {
            editableLayers = new L.geoJson();
        }

        var mapOptions = {
            center: center,
            zoom: $el.data("zoom") || 12,
            minZoom: $el.data("min-zoom"),
            maxZoom: $el.data("max-zoom"),
            maxBounds: maxBounds
        };

        if (!editable) {
            mapOptions.dragging = false;
            mapOptions.touchzoom = false;
            mapOptions.scrollWheelZoom = false;
            mapOptions.doubleClickZoom = false;
            mapOptions.boxZoom = false;
            mapOptions.tap = false;
            mapOptions.keyboard = false;
            mapOptions.zoomControl = false;
        }

        // only show attributions if the map is big enough
        // (otherwise, it gets in the way)
        if ($map.width() * $map.height() < 10000) {
            mapOptions.attributionControl = false;
        }

        var map = L.map($map.get(0), mapOptions);
        map.addLayer(editableLayers);

        if (center) {
            // if we have more than one point, make the map show everything
            var bounds = editableLayers.getBounds();
            if (!bounds.getNorthEast().equals(bounds.getSouthWest())) {
                map.fitBounds(bounds);
            }
        } else {
            // look up user's location by IP address
            $.getJSON("//ip-api.com/json/?callback=?", function(data) {
                map.setView([data["lat"], data["lon"]], 12);
            }).fail(function() {
                map.setView([0, 0], 1);
            });
        }

        // set up tiles
        var mapboxVersion = window.MAPBOX_ACCESS_TOKEN ? 4 : 3;
        L.tileLayer('//{s}.tiles.mapbox.com/v'+mapboxVersion+'/'+MAPBOX_MAP_ID+'/{z}/{x}/{y}.png?access_token='+window.MAPBOX_ACCESS_TOKEN, {
            attribution: 'Map data &copy; <a href="//openstreetmap.org">OpenStreetMap</a> contributors, <a href="//creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="//mapbox.com">Mapbox</a>',
            maxZoom: 18
        }).addTo(map);


        // everything below here is to set up editing, so if we're not editable,
        // we can just return early.
        if (!editable) {
            return true;
        }

        // set up Leaflet.draw editor
        var drawOptions = {
            draw: {
                // circles are not geometries in geojson
                circle: false
            },
            edit: {
                featureGroup: editableLayers
            }
        };

        if ($.inArray(geometryType, ["POINT", "MULTIPOINT"]) > -1) {
            drawOptions.draw.polyline = false;
            drawOptions.draw.polygon = false;
            drawOptions.draw.rectangle = false;
        } else if ($.inArray(geometryType, ["LINESTRING", "MULTILINESTRING"]) > -1) {
            drawOptions.draw.marker = false;
            drawOptions.draw.polygon = false;
            drawOptions.draw.rectangle = false;
        } else if ($.inArray(geometryType, ["POLYGON", "MULTIPOLYGON"]) > -1) {
            drawOptions.draw.marker = false;
            drawOptions.draw.polyline = false;
        }
        var drawControl = new L.Control.Draw(drawOptions);
        map.addControl(drawControl);

        if (window.google) {
            var geocoder = new google.maps.Geocoder();

            function googleGeocoding(text, callResponse) {
                geocoder.geocode({address: text}, callResponse);
            }

            function filterJSONCall(rawjson) {
                var json = {}, key, loc, disp = [];
                for (var i in rawjson) {
                    key = rawjson[i].formatted_address;
                    loc = L.latLng(rawjson[i].geometry.location.lat(),
                                   rawjson[i].geometry.location.lng());
                    json[key] = loc;
                }
                return json;
            }

            map.addControl(new L.Control.Search({
                callData: googleGeocoding,
                filterJSON: filterJSONCall,
                markerLocation: true,
                autoType: false,
                autoCollapse: true,
                minLength: 2,
                zoom: 10
            }));
        }


        // save when the editableLayers are edited
        var saveToTextArea = function() {
            var geo = editableLayers.toGeoJSON();
            if (geo.features.length === 0) {
                $el.val("");
                return true
            }
            if (multiple) {
                var coords = $.map(geo.features, function(feature) {
                    return [feature.geometry.coordinates];
                });
                geo = {
                    "type": geometryType,
                    "coordinates": coords
                };
            } else {
                geo = geo.features[0].geometry;
            }
            $el.val(JSON.stringify(geo));
        };

        // handle creation
        map.on('draw:created', function (e) {
            if (!multiple) {
                editableLayers.clearLayers();
            }
            editableLayers.addLayer(e.layer);
            saveToTextArea();
        });
        map.on('draw:edited', saveToTextArea);
        map.on('draw:deleted', saveToTextArea);
    };

    // make x-editable's POST compatible with WTForms
    // for x-editable, x-editable-combodate, and x-editable-boolean cases
    var overrideXeditableParams = function(params) {
        var newParams = {};
        newParams['list_form_pk'] = params.pk;
        newParams[params.name] = params.value;
        if ($(this).data('csrf')) {
            newParams['csrf_token'] = $(this).data('csrf');
        }
        return newParams;
    };

    this.fieldStyles['x-editable'] = function($el, name) {
        $el.editable({params: overrideXeditableParams});
    };

    this.fieldStyles['x-editable-combodate'] = function($el, name) {
        $el.editable({
            params: overrideXeditableParams,
            combodate: {
                // prevent minutes from showing in 5 minute increments
                minuteStep: 1
            }
        });
    };

    this.fieldStyles['x-editable-select2-multiple'] = function($el, name) {
        $el.editable({
            params: overrideXeditableParams,
            ajaxOptions: {
                // prevents keys with the same value from getting converted into arrays
                traditional: true
            },
            select2: {
                multiple: true
            },
            display: function(value) {
                // override to display text instead of ids on list view
                var html = [];
                var data = $.fn.editableutils.itemsByValue(value, $el.data('source'), 'id');

                if(data.length) {
                    $.each(data, function(i, v) { html.push($.fn.editableutils.escape(v.text)); });
                    $(this).html(html.join(', '));
                } else {
                    $(this).empty();
                }
            }
        });
    };

    this.fieldStyles['x-editable-boolean'] = function($el, name) {
        $el.editable({
            params: overrideXeditableParams,
            display: function(value, sourceData, response) {
                // display new boolean value as an icon
                if(response) {
                    if(value == '1') {
                        $(this).html('<span class="fa fa-check-circle glyphicon glyphicon-ok-circle icon-ok-circle"></span>');
                    } else {
                        $(this).html('<span class="fa fa-minus-circle glyphicon glyphicon-minus-sign icon-minus-sign"></span>');
                    }
                }
            }
        });
    };

    /**
     * Process data-role attribute for the given input element. Feel free to override
     *
     * @param {Selector} $el jQuery selector
     * @param {String} name data-role value
     */
    this.applyStyle = function($el, name) {
        // Process converters first
        for (var conv in fieldConverters) {
            var fieldConv = fieldConverters[conv];

            if (fieldConv($el, name))
                return;
        }

        styleFunc = this.fieldStyles[name];
        if (styleFunc) {
            styleFunc($el, name);
        }
    };

    /**
     * Add inline form field
     *
     * @method addInlineField
     * @param {Node} el Button DOM node
     * @param {String} elID Form ID
     */
    this.addInlineField = function(el, elID) {
        // Get current inline field
        var $el = $(el).closest('.inline-field');
        // Figure out new field ID
        var id = elID;

        var $parentForm = $el.parent().closest('.inline-field');

        if ($parentForm.hasClass('fresh')) {
            id = $parentForm.attr('id');
            if (elID) {
                id += '-' + elID;
            }
        }

        var $fieldList = $el.find('> .inline-field-list');
        var maxId = 0;

        $fieldList.children('.inline-field').each(function(idx, field) {
            var $field = $(field);

            var parts = $field.attr('id').split('-');
            idx = parseInt(parts[parts.length - 1], 10) + 1;

            if (idx > maxId) {
                maxId = idx;
            }
        });

        var prefix = id + '-' + maxId;

        // Get template
        var $template = $($el.find('> .inline-field-template').text());

        // Set form ID
        $template.attr('id', prefix);

        // Mark form that we just created
        $template.addClass('fresh');

        // Fix form IDs
        $('[name]', $template).each(function(e) {
            var me = $(this);

            var id = me.attr('id');
            var name = me.attr('name');

            id = prefix + (id !== '' ? '-' + id : '');
            name = prefix + (name !== '' ? '-' + name : '');

            me.attr('id', id);
            me.attr('name', name);
        });

        $template.appendTo($fieldList);

        // Select first field
        $('input:first', $template).focus();

        // Apply styles
        this.applyGlobalStyles($template);
    };

    /**
     * Apply global input styles.
     *
     * @method applyGlobalStyles
     * @param {Selector} jQuery element
     */
    this.applyGlobalStyles = function(parent) {
        var self = this;

        $('[data-role]', parent).each(function() {
            var $el = $(this);
            self.applyStyle($el, $el.attr('data-role'));
        });
    };

    /**
     * Add a field converter for customizing styles
     *
     * @method addFieldConverter
     * @param {converter} function($el, name)
     */
    this.addFieldConverter = function(converter) {
        fieldConverters.push(converter);
    };
};

// Add on event handler
$('body').on('click', '.inline-remove-field' , function(e) {
    e.preventDefault();

    var form = $(this).closest('.inline-field');
    form.remove();
});

// Expose faForm globally
var faForm = window.faForm = new AdminForm();

