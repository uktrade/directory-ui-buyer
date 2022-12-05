'use strict';
const path = require('path');
const gulp = require('gulp');
const sass = require('gulp-sass')(require('node-sass'));

const PROJECT_DIR = path.resolve(__dirname);
const SASS_FILES = `${PROJECT_DIR}/enrolment/static/sass/*.scss`;
const CSS_DIR = `${PROJECT_DIR}/enrolment/static`;

gulp.task('sass', function () {
  return gulp.src(SASS_FILES, {sourcemaps: true})
    .pipe(sass({
      outputStyle: 'compressed'
    }).on('error', sass.logError))
    .pipe(gulp.dest(CSS_DIR, {sourcemaps: './maps'}));
});

gulp.task('default', gulp.series('sass'));
