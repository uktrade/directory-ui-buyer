#!/bin/bash
# This script will render the project css files.

# put the path of library scss files we want to incluide
libraries="\
	--load-path node_modules/govuk_frontend_toolkit/stylesheets \
	--load-path node_modules/trade_elements/sass \
	--load-path enrolment/static/sass \
	--load-path node_modules/govuk-elements-sass/public/sass \
"

# put the path of source code files we want to include, and where we want them
# to be exported to e.g., input.scss:output.css
input_output_map="\
	enrolment/static/sass/main.scss:enrolment/static/main.css \
	enrolment/static/sass/enrolment.scss:enrolment/static/enrolment.css \
	enrolment/static/sass/company-profile-details.scss:enrolment/static/company-profile-details.css \
	enrolment/static/sass/company-profile-form.scss:enrolment/static/company-profile-form.css \
	enrolment/static/sass/user-profile-details.scss:enrolment/static/user-profile-details.css \
	enrolment/static/sass/user-profile-edit-form.scss:enrolment/static/user-profile-edit-form.css \
"

dev_command="\
	sass \
	--style expanded \
	--line-numbers \
"

watch_command="\
	sass \
	--style expanded \
	--line-numbers \
	--watch \
"

prod_command="sass --style compressed"

eval 'rm enrolment/static/*.css profile/static/*.css'
if [ "$1" == "dev" ]; then
	eval $dev_command$libraries$input_output_map
elif [ "$1" == "prod" ]; then
	eval $prod_command$libraries$input_output_map
elif [ "$1" == "watch" ]; then
	eval $watch_command$libraries$input_output_map
fi
