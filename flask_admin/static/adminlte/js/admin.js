"use strict"; // Ensure that all variables are defined!

/*
 * This admin.js file should only contain functions that are specific to flask-admin-related
 * behaviors. Always keep in mind what the domain/usability of your functions is - meaning
 * that you should separate out the project/app-specific functions to the project's admin.js
 * and widget/UI related functions to the flask-admin-widgets admin.js, if you decide to
 * include that package in your solution.
 */

// Trumbowyg
$(function() {
    function real_length(str) { // text length without html tags
        var el = document.createElement("div");
        el.innerHTML = str;
        return $(el).text().length;
    }
    function update_max_length(feedback_box, current_length)
    {
        var box_text = feedback_box.html();
        var max_length = parseInt(box_text.match(/\/(\d+)$/)[1]);
        var new_text = box_text.replace(/\d+\//g, current_length+"/");
        feedback_box.html(new_text);

        current_length = parseInt(current_length);
        if(current_length == max_length)
        {
            feedback_box.addClass("maxlength-full");
            feedback_box.removeClass("maxlength-overflow");
        }
        else if(current_length > max_length)
        {
            feedback_box.addClass("maxlength-full");
            feedback_box.addClass("maxlength-overflow");
        }
        else
        {
            feedback_box.removeClass("maxlength-full");
            feedback_box.removeClass("maxlength-overflow");
        }
    }
    function setup_trumbowyg(objects)
    {
        objects.each(function() {
            $(this).trumbowyg({
                btns: eval($(this).data("btns")) || [['bold', 'italic', 'viewHTML']],
                autogrow: $(this).data("autogrow") || true,
                semantic: $(this).data("semantic") || false,
                removeformatPasted: $(this).data("removeformatPasted") || true,
            }).each(function () {
                var height = 12 + (20 * parseInt($(this).attr("rows")));
                if(height <= 0) { height = 32; }
                $(this).parent().find(".trumbowyg-editor").css("min-height", height);
                $(this).height(height);
            }).on("tbwinit", function() {
                var $html = $(this).trumbowyg('html');

                if ($html.lastIndexOf("<ul>") > -1){
                    $html = $html.replace(new RegExp("<ul>", "g"), "<ul class='bullet-list'>");  
                }

                if ($html.lastIndexOf("<ol>") > -1){
                    $html = $html.replace(new RegExp("<ol>", "g"), "<ol class='bullet-list'>");                    
                }

                $(this).trumbowyg('html', $html);
 
                var current_length = real_length($html);
                var feedback_box = $(".maxlength-feedback", $(this).parent());
                if(feedback_box.length > 0)
                {
                    feedback_box.css("right", "4px");
                    update_max_length(feedback_box, current_length);
                }
            }).on("tbwchange", function() {
                var current_length = real_length($(this).trumbowyg('html'));
                var feedback_box = $(".maxlength-feedback", $(this).parent());
                if(feedback_box.length > 0)
                {
                    update_max_length(feedback_box, current_length);
                }
            });
        });
    }

    // On Page Load
    setup_trumbowyg($("textarea[data-role='trumbowyg']"));

    // On List Field Add
    $("a[onclick]").filter(function() {
        return $(this).attr("onclick").match(/faForm\.addInlineField.+?/);
    }).on("click", function(e) {
        var parent = $(this).parent();
        var new_form = $(".inline-field-list > .inline-field", parent).last();
        setup_trumbowyg($("textarea[data-role='trumbowyg']", new_form));
    });
});
// End trumbowyg

// Make select2 lists sortable
if ($().sortable) {
    $(function() {

        // Make inline field lists sortable. Sorting is remembered by updating all IDs (along with name and label for's),
        // for every input element (includes input, textarea, select, and button) to the new order.
        //
        // For example. if each inline field list has a field named "categories-<some index>-title", after a sort is
        // performed, this goes through and updates all IDs so the top inline field has its IDs all become 0, the next
        // has all its IDs become 1, and so on.
        //
        //    INITIAL SORT                          AFTER 2 TO THE TOP                   AFTER JS EXECUTES
        //    categories-0-title       ->           categories-2-title        ->         categories-0-title
        //    categories-1-title   (user moves)     categories-0-title   (stop method)   categories-1-title
        //    catetories-2-title   (2 to the top)   categories-1-title   (is executed)   categories-2-title
        //
        $("div.inline-field-list").css("overflow", "auto");
        $("div.inline-field-list").css("overflow-x", "hidden");

        /** Commented out -- CJ DiMaggio 3/8/2017
        $("div.inline-field-list").sortable({
            stop: function( event, ui ) {
                var matches = ui.item.attr("id").match(/(.+?)-\d+$/);
                if(matches[1] !== undefined)
                {
                    var prefix = matches[1];

                    var i = 0;
                    $(this).children(".inline-field").each(function() {
                        var update_id_regex = new RegExp("("+prefix+"-)[0-9]+(.*)?", "i");

                        // Update the parent id
                        $(this).attr("id", $(this).attr("id").replace(update_id_regex, "$1"+i+"$2"));

                        // Update all input and label fields
                        var attributes = ["id", "name", "for"];
                        $( ":input, label", this ).each(function() {
                            var field = $(this);
                            $.each(attributes, function (index, value) {
                                if($(field).attr(value) !== undefined)
                                {
                                    $(field).attr(value, $(field).attr(value).replace(update_id_regex, "$1"+i+"$2"));
                                }
                            });
                        });

                        i = i + 1;
                    });
                }
            }
        });
        **/

        // CTRL+s or COMMAND+s does a 'Save and Continue Editing'
        $(window).bind('keydown', function(event) {
            if (event.ctrlKey || event.metaKey) {
                switch (String.fromCharCode(event.which).toLowerCase()) {
                case 's':
                    event.preventDefault();
                    $("input[name='_continue_editing']").click();
                    break;
                }
            }
        });

        // Disable Enter key from submitting form
        $("form input[type='text']").keydown(function (e) {
            if (e.keyCode == 13) {
                e.preventDefault();
                return false;
            }
        });

        // Autosizing for text areas
        // On Page Load
        $("textarea[data-role='autosize']").each(function() {
            autosize($(this));
        });
        // On List Field Add
        $("a[onclick]").filter(function() {
            return $(this).attr("onclick").match(/faForm\.addInlineField.+?/);
        }).on("click", function(e) {
            var parent = $(this).parent();
            var new_form = $(".inline-field-list > .inline-field", parent).last();
            $("textarea[data-role='autosize']", new_form).each(function() {
                autosize($(this));
            });
        });

        // For Custom InputFields and TextAreaFields which support the data-maxlength attribute
        // All options can be set with data-* attributes, falling
        // back to defaults if not given.
        //
        // http://keith-wood.name/maxlengthRef.html
        //
        // On Page Load
        $("*[data-maxlength-strict]").each(function() {
            $( this ).maxlength({
                max: $(this).data("maxlength") || $(this).attr("maxlength"),
                truncate: $(this).data('truncate') || false,
                feedbackText: $(this).data("feedbackText") || "{c}/{m}",
                overflowText: $(this).data("overflowText") || "{c}/{m}"
            });
        });
        // On List Field Ass
        $("a[onclick]").filter(function() {
            return $(this).attr("onclick").match(/faForm\.addInlineField.+?/);
        }).on("click", function(e) {
            var parent = $(this).parent();
            var new_form = $(".inline-field-list > .inline-field", parent).last();
            $("*[data-maxlength-strict]", new_form).each(function() {
                $( this ).maxlength({
                    max: $(this).data("maxlength") || $(this).attr("maxlength"),
                    truncate: $(this).data('truncate') || false,
                    feedbackText: $(this).data("feedbackText") || "{c}/{m}",
                    overflowText: $(this).data("overflowText") || "{c}/{m}"
                });
            });
        });
    });
};

// Make select2 lists sortable
$(function() {
    // Select v4 uses normal select fields (not hidden input fields). These are not sortable. To achieve the sort,
    // the individual select options need to be removed and added in the correct order.
    //
    $("ul.select2-selection__rendered").sortable({
        update: function( event, ui ) {
            var select = $("select", $(this).parent().parent().parent().parent()); // TODO: Make this cleaner, closest() doesn't seem to wrok

            var item_moved = $(ui.item).attr("title");
            var options = [];
            $(".select2-selection__choice", this).each(function(index) {
                var title = $(this).attr("title");
                var option = $("option", select).filter(function () { return $(this).html() == title; });
                options[index] = option[0];
            });

            $("option:selected", select).remove();
            options = options.reverse();
            for(var index in options)
            {
                $(select).prepend(options[index]);
            }
        }
    });

    // Make inline field lists sortable. Sorting is remembered by updating all IDs (along with name and label for's),
    // for every input element (includes input, textarea, select, and button) to the new order.
    //
    // For example. if each inline field list has a field named "categories-<some index>-title", after a sort is
    // performed, this goes through and updates all IDs so the top inline field has its IDs all become 0, the next
    // has all its IDs become 1, and so on.
    //
    //    INITIAL SORT                          AFTER 2 TO THE TOP                   AFTER JS EXECUTES
    //    categories-0-title       ->           categories-2-title        ->         categories-0-title
    //    categories-1-title   (user moves)     categories-0-title   (stop method)   categories-1-title
    //    categories-2-title   (2 to the top)   categories-1-title   (is executed)   categories-2-title
    //
    // TODO: Update list styling so sorting can only be done on the top header (include icon for intuitiveness)
    //
    $("div.inline-field-list").css("overflow",   "auto");
    $("div.inline-field-list").css("overflow-x", "hidden");
//    $("div.inline-field-list").sortable({
//        update: function( event, ui ) {
//            var matches = ui.item.attr("id").match(/(.+?)-\d+$/);
//            if(matches[1] !== undefined)
//            {
//                var prefix = matches[1];
//                var update_id_regex = new RegExp("("+prefix+"-)[0-9]+(.*)?", "i");
//
//                var i = 0;
//                $(this).children(".inline-field").each(function() {
//                    // Update the parent id
//                    $(this).attr("id", $(this).attr("id").replace(update_id_regex, "$1"+i+"$2"));
//
//                    // Update all input and label fields
//                    var attributes = ["id", "name", "for"];
//                    $( ":input, label", this ).each(function() {
//                        var field = $(this);
//                        $.each(attributes, function (index, value) {
//                            if($(field).attr(value) !== undefined)
//                            {
//                                $(field).attr(value, $(field).attr(value).replace(update_id_regex, "$1"+i+"$2"));
//                            }
//                        });
//                    });
//
//                    i = i + 1;
//                });
//            }
//            $(this).sortable("refreshPositions").sortable("refresh");
//        }
//    });
    $(window).on("mouseup", function() {
        $("div.inline-field-list").each(function() {
            if($(this).hasClass('ui-sortable'))
            {
                $(this).sortable("enable");
            }
        });
    });

    // CTRL+s or COMMAND+s does a 'Save'
    $(window).bind('keydown', function(event) {
        if (event.ctrlKey || event.metaKey) {
            switch (String.fromCharCode(event.which).toLowerCase()) {
            case 's':
                event.preventDefault();
                //$("input[name='_continue_editing']").click();
                $("input[value='Save']").click();
                break;
            }
        }
    });

    // Disable Enter key from submitting a form on all input fields except inputs with type="search"
    $("input[type!='search']").filter("input[type!='password']").on("keydown", function (e) {
        if (e.keyCode == 13) {
            e.preventDefault();
            return false;
        }
    });

    // Autosizing for text areas
    // On Page Load
    $("textarea[data-role='autosize']").each(function() {
        autosize($(this));
    });
    // On List Field Add
    $("a[onclick]").filter(function() {
        return $(this).attr("onclick").match(/faForm\.addInlineField.+?/);
    }).on("click", function(e) {
        var parent = $(this).parent();
        var new_form = $(".inline-field-list > .inline-field", parent).last();
        $("textarea[data-role='autosize']", new_form).each(function() {
            autosize($(this));
        });
    });

    // For FAWInputFields and FAWTextAreaFields
    // All options can be set with data-* attributes, falling
    // back to defaults if not given.
    //
    // http://keith-wood.name/maxlengthRef.html
    //
    // On Page Load
    $("*[data-maxlength='maxlength']").each(function() {
        $( this ).maxlength({
            max: $(this).data("max") || $(this).attr("maxlength"),
            truncate: $(this).data('truncate') || false,
            showFeedback: $(this).data("showFeedback") || true,
            feedbackTarget: $(this).data("feedbackTarget") || null,
            feedbackText: $(this).data("feedbackText") || "{c}/{m}",
            overflowText: $(this).data("overflowText") || "{c}/{m}",
        });
    });
    // On List Field Add
    $("a[onclick]").filter(function() {
        return $(this).attr("onclick").match(/faForm\.addInlineField.+?/);
    }).on("click", function(e) {
        var parent = $(this).parent();
        var new_form = $(".inline-field-list > .inline-field", parent).last();
        $("*[data-maxlength='maxlength']", new_form).each(function() {
            $( this ).maxlength({
                max: $(this).data("max") || $(this).attr("maxlength"),
                truncate: $(this).data('truncate') || false,
                showFeedback: $(this).data("showFeedback") || true,
                feedbackTarget: $(this).data("feedbackTarget") || null,
                feedbackText: $(this).data("feedbackText") || "{c}/{m}",
                overflowText: $(this).data("overflowText") || "{c}/{m}",
            });
        });
    });
});
// End select2 customization

