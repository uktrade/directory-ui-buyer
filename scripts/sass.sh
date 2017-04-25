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
	enrolment/static/sass/supplier-profile-details.scss:enrolment/static/supplier-profile-details.css \
	enrolment/static/sass/landing-page.scss:enrolment/static/landing-page.css \
	enrolment/static/sass/landing-page-old.scss:enrolment/static/landing-page-old.css \
"

prod_command="sass --style compressed"

eval 'rm enrolment/static/*.css profile/static/*.css'
eval $prod_command$libraries$input_output_map
