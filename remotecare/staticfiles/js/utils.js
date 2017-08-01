var ArrayFunctions = {
    remove_from_array: function(array, array1) {
        //Removes alle elements from array1 from array.

        newArray = [];
        for (var i = 0; i < array.length; i++) {
            var found = false;
            var j = 0;
            while (j < array1.length && !found) {

                if (array[i] == array1[j])
                    found = true;
                j++;
            }

            if (!found)
                newArray.push(array[i]);
        }

        return newArray;
    },
    make_array_unique: function(array) {
        newArray = [];

        for (var i = 0; i < array.length; i++) {
            var found = false;
            var j = 0;
            while (j < newArray.length && !found) {
                if (newArray[j] == array[i])
                    found = true;
                j++;
            }
            if (!found)
                newArray.push(array[i]);
        }

        return newArray;
    }
}


var FormField = {
    init: function(content) {
        $(content).find('select.choice_display').change(function() {
            FormField.selectField(this);

        });

        $(content).find('input:checkbox.choice_display').change(function() {
            FormField.checkBox(this);
        });

        FormField.initOnce(content);
    },
    initOnce: function(content) {
        //INIT ONLY ONCE!
        //only necessary to hide fields, fields are default shown..

        $(content).find('select.choice_display').each(function() {

            FormField.initSelectField(this);


        });

        $(content).find('input:checkbox.choice_display').each(function() {
            if (this.id.indexOf('_0') > -1) {
                FormField.initCheckBox(this);
            }
        });
    },
    initSelectField: function(field) {
        var choices = eval($(field).attr('choices'))[0];
        var show_fields = [];
        var value = $(field).val();
        var form = field.form;
        var selected_choices = choices[value];


        $.each(choices, function(attr, item) {

            if (attr != value) {
                //remove all entries from 'item' which are also in the selected_choices list.
                //NEEDED in case there are two options which have the same entries within 'choices'


                if (selected_choices != null)
                    item = ArrayFunctions.remove_from_array(item, selected_choices);

                $.each(item, function(i, input_name) {
                    if (jQuery.inArray(input_name, show_fields) == -1) {
                        var fieldset = $('.hi-light.' + input_name, form).hide();
                    }
                });
            }
        });
    },
    initCheckBox: function(field) {
        var form = field.form;
        var hide_fields = [];
        var show_fields = [];

        var choices = eval($(field).attr('choices'));
        //Not check every checkbox item, instead look for items within choices!
        if (choices != undefined) {
            for (key in choices[0]) {
                var checkbox = $(field.form).find('[name=' + $(field).attr('name') + '][value=' + key + ']')[0];
                var fields = $(choices).attr(key);
                if (checkbox.checked) {
                    show_fields = show_fields.concat(fields);
                }
                else {
                    hide_fields = hide_fields.concat(fields);
                }
            }
        }
        hide_fields = ArrayFunctions.make_array_unique(hide_fields);
        show_fields = ArrayFunctions.make_array_unique(show_fields);

        //REMOVE THE FIELDS FROM SHOW_FIELDS FROM HIDE_FIELDS.
        if (show_fields.length > 0)
            hide_fields = ArrayFunctions.remove_from_array(hide_fields, show_fields);

        $.each(hide_fields, function(i, input_name) {
            var fieldset = $('.hi-light.' + input_name, form).hide();
        });
    },
    selectField: function(field) {


        var choices = eval($(field).attr('choices'))[0];
        var value = $(field).val();
        var show_fields = [];
        var hide_fields = [];


        //console.log('- ' + value);

        $.each(choices, function(attr, item) {

            if (attr == value) {
                $.each(item, function(i, input_name) {
                    show_fields.push(input_name);
                });
            } else {
                $.each(item, function(i, input_name) {
                    hide_fields.push(input_name);
                });
            }
        });



        //console.log(' --- ' + field.id +  ' --- hide: ' + hide_fields + ' Show ' + show_fields);

        hide_fields = ArrayFunctions.make_array_unique(hide_fields);
        show_fields = ArrayFunctions.make_array_unique(show_fields);



        if (show_fields.length > 0)
            hide_fields = ArrayFunctions.remove_from_array(hide_fields, show_fields);



        //console.log(' ### ' + field.id +  ' --- hide: ' + hide_fields + ' Show ' + show_fields);

        FormField.hideFields(field, hide_fields);

        FormField.showFields(field, show_fields);



    },
    checkBox: function(field) {
        var choices = eval($(field).attr('choices'));
        var show_fields = [];
        var hide_fields = [];

        if (choices != undefined) {
            for (key in choices[0]) {
                var checkbox = $(field.form).find('[name=' + $(field).attr('name') + '][value=' + key + ']')[0];
                var fields = $(choices).attr(key);
                if (checkbox.checked) {
                    show_fields = show_fields.concat(fields);
                }
                else {
                    hide_fields = hide_fields.concat(fields);
                }
            }
        }
        show_fields = ArrayFunctions.make_array_unique(show_fields);
        hide_fields = ArrayFunctions.make_array_unique(hide_fields);

        //if the field is in show_fields, remove from hide_fields!!
        if (show_fields.length > 0)
            hide_fields = ArrayFunctions.remove_from_array(hide_fields, show_fields);

        //console.log(field.id, 'show', show_fields);
        //console.log(field.id, 'hide', hide_fields);

        FormField.hideFields(field, hide_fields);
        FormField.showFields(field, show_fields);
    },
    hideFields: function(field, hide_fields) {
        $.each(hide_fields, function(i, input_name) {
            var form = field.form;

            //var fieldset = $('[name^=' + input_name + ']', form).closest('.hi-light').hide();
            var fieldset = $('.hi-light.' + input_name, form).hide();
            $(fieldset).find('select').each(function() {
                $(this).val('');
            }).change();

            $(fieldset).find('input:text').each(function() {
                $(this).val('');
            });

            //FIRST NEED TO SET ALL TO UNCHECKED BEFORE EXECUTING CHANGE FUNCTION!!
            $(fieldset).find(':checkbox').each(function() {
                this.checked = false;
            });

            $(fieldset).find(':checkbox').each(function() {
                if (this.id.indexOf('_0') > -1) {
                    FormField.checkBox(this);

                    //trigger change event, which can be used in other places to change related/coupled
                    //selection controls.
                    $(this).change();
                }
            });
        });
    },
    showFields: function(field, show_fields) {



        $.each(show_fields, function(i, input_name) {
            var form = field.form;
            //var fieldset = $(form).find('[name^=' + input_name + ']').closest('.hi-light');
            var fieldset = $('.hi-light.' + input_name, form);

            fieldset.show();



            //NEEDED TO HIDE 'OTHER' FIELDS..

            $(fieldset).find(':checkbox[id*=_0].choice_display').each(function() {
                FormField.initCheckBox(this);
            });
        });


        //
    },
    onChange: function() {
    },
    checkBoxOnChange: function() {
    }
}


var FormFieldInit = {
    init: function(content) {
        $(content).find('select.choice_display').change(function() {

            FormField.selectField(this);
        });

        $(content).find('input:checkbox.choice_display').change(function() {
            FormField.checkBox(this);
        });

        FormField.initOnce(content);
    }
}


var OtherChoiceSelect = {
    initial: function(content) {
        //Change function..
        $(content).find('select.other-choice-select').change(function() {
            if (this.value == 'other') $('.other-choice-text', this.parentNode.parentNode).show();
            else $('.other-choice-text', this.parentNode.parentNode).hide();
        });

        //init once.
        $(content).find('select.other-choice-select').each(function() {
            var label = $(this.parentNode).prev();
            var specify_label = $('.specify-label', label);
            //Check if already added..
            if ($(specify_label).length == 0)
            {
                label.append('<br><label class="other-choice-text specify-label"></label>');
                if (this.value == 'other') {
                    $('.other-choice-text', this.parentNode.parentNode).slideDown();
                }
                else {
                    $('.other-choice-text', this.parentNode.parentNode).hide();
                }
            }
        });

    }
}

var DateTime = {
    init: function(content) {
        $('span.date_field', content).each(function() {
            var today_link = $('<a href="#" onclick="DateTime.today(this, event);">Vandaag</a>');
            var datepicker_link = $('<input type="hidden" class="dp" />');

            if ($(this).prev().attr('id').indexOf('date_of_birth') == -1)
            {
                $(this).append(today_link);
                $(this).append(' | ');
            }
            $(this).append(datepicker_link);

        });
        $(".dp").datepicker({

            buttonImageOnly: false,
            buttonText: '',
            showOn: 'both',
            onSelect: function(dateText, inst) {
                DateTime.setToday(this, new Date(dateText));
            }
        });

		$(".ui-datepicker").hide();
    },
    setToday: function(object, date) {
        $(object).closest('.field').find('[id$=year]').val(date.getFullYear());
        $(object).closest('.field').find('[id$=month]').val(date.getMonth() + 1);
        $(object).closest('.field').find('[id$=day]').val(date.getDate());
    },
    today: function(object, event) {
        $.Event(event).preventDefault();
        this.setToday(object, new Date())
    },
    now: function(object, event) {
        $.Event(event).preventDefault();
        now = new Date();
        $(object).closest('.field').find('[id$=hour]').val(now.getHours());
        $(object).closest('.field').find('[id$=minute]').val(now.getMinutes());
    }
}



var DocumentInitial = {
    init: function(content) {
        FormFieldInit.init(content);
        OtherChoiceSelect.initial(content);
        //ListSelector.initial(content);
        DateTime.init(content);

        if ($.browser.msie) {
            $('input:checkbox').click(function() {
                this.blur();
                this.focus();
            });
        }

        //add autocomplete=off to all forms
        $('form').each(function() {
            $(this).attr('autocomplete', 'off');
        });

        $('[name=mobile_number2]').bind('paste', function(e) {
            e.preventDefault();
        });
        $('[name=person_email2]').bind('paste', function(e) {
            e.preventDefault();
        });

    }
}




$(document).ready(function() {
    DocumentInitial.init();
});

