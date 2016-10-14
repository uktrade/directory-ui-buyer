#!/bin/bash
# This script will render the project css files.

# put the path of library scss files we want to incluide
libraries="\
	--load-path node_modules/govuk_frontend_toolkit/stylesheets \
	--load-path node_modules/trade_elements/sass \
	--load-path registration/static/sass \
	--load-path node_modules/govuk-elements-sass/public/sass \
"

# put the path of source code files we want to include, and where we want them
# to be exported to e.g., input.scss:output.css
input_output_map="\
	registration/static/sass/main.scss:registration/static/main.css \
	registration/static/sass/registration.scss:registration/static/registration.css \
	registration/static/sass/company-profile-details.scss:registration/static/company-profile-details.css \
	registration/static/sass/company-profile-form.scss:registration/static/company-profile-form.css \
	profile/static/sass/user-profile-details.scss:profile/static/user-profile-details.css \
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

eval 'rm registration/static/*.css profile/static/*.css'
if [ "$1" == "dev" ]; then
	eval $dev_command$libraries$input_output_map
elif [ "$1" == "prod" ]; then
	eval $prod_command$libraries$input_output_map
elif [ "$1" == "watch" ]; then
	eval $watch_command$libraries$input_output_map
fi