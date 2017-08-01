# -*- coding: utf-8 -*-
"""
The periodic controls to be filled in by patients consists of one or more \
disease specific questionnaires. Currently the questionnaires are divided \
into the following steps:
    - How are you doing? (start questionnaire)
    - Disease activity
    - Quality of life
    - Quality of health care (optional, included once per year)
    - Appointment, blood taken (finish questionnaire)

Some diseases don't have questionnaires for the disease activity step.
For the urgent questionnaires the first two steps are replaced
with a 'direct appointment' and a 'description of the problem' step.

Every questionnaire is stored as one model and multiple forms coupled to
the questionnaire model are included into the
:class:`apps.questionnaire.wizards.QuestionnaireWizard` to display the forms
after eachother.

The wizard uses a :class:`apps.questionnaire.storage.DatabaseStorage` instance
to store the filled in information. All posted form data is saved
automatically to allow the user to stop and later return to finish the
questionnaire. The storage allows saving unclean (post) data for this purpose.
When all steps/questionnaires are succesfully filled in all unclean data is
run through the clean methods of the forms and the cleaned data is
stored in the questionnaire models.
"""
