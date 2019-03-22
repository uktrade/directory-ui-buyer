'use strict';
const path = require('path');
const gulp = require('gulp');
const sass = require('gulp-sass');
const sourcemaps = require('gulp-sourcemaps');

const PROJECT_DIR = path.resolve(__dirname);
const SASS_FILES = `${PROJECT_DIR}/enrolment/static/sass/*.scss`;
const CSS_DIR = `${PROJECT_DIR}/enrolment/static`;

gulp.task('sass', function () {
  return gulp.src(SASS_FILES)
    .pipe(sourcemaps.init())
    .pipe(sass({
      outputStyle: 'compressed'
    }).on('error', sass.logError))
    .pipe(sourcemaps.write('.', {includeContent: false}))
    .pipe(gulp.dest(CSS_DIR));
});

gulp.task('default', gulp.series('sass'));
