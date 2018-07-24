@echo off

REM  HITACHI VANTARA PROPRIETARY AND CONFIDENTIAL
REM
REM  Copyright 2017 - 2018 Hitachi Vantara. All rights reserved.
REM
REM  NOTICE: All information including source code contained herein is, and
REM  remains the sole property of Hitachi Vantara and its licensors. The intellectual
REM  and technical concepts contained herein are proprietary and confidential
REM  to, and are trade secrets of Hitachi Vantara and may be covered by U.S. and foreign
REM  patents, or patents in process, and are protected by trade secret and
REM  copyright laws. The receipt or possession of this source code and/or related
REM  information does not convey or imply any rights to reproduce, disclose or
REM  distribute its contents, or to manufacture, use, or sell anything that it
REM  may describe, in whole or in part. Any reproduction, modification, distribution,
REM  or public display of this information without the express written authorization
REM  from Hitachi Vantara is strictly prohibited and in violation of applicable laws and
REM  international treaties. Access to the source code contained herein is strictly
REM  prohibited to anyone except those individuals and entities who have executed
REM  confidentiality and non-disclosure agreements or other agreements with Hitachi Vantara,
REM  explicitly covering such access.

@REM
@REM WARNING: Pentaho Report Designer needs JDK 1.7 or newer to run.
@REM
setlocal
cd /D %~dp0
set CONSOLE=1

REM Special console/debug options when called from report-designer.bat or report-designer-debug.bat
if "%CONSOLE%"=="1" set PENTAHO_JAVA=java
if not "%CONSOLE%"=="1" set PENTAHO_JAVA=javaw

if "%_PENTAHO_JAVA_HOME%" == "" goto callSetEnv
set PENTAHO_JAVA_HOME=%_PENTAHO_JAVA_HOME%

:callSetEnv
call "%~dp0set-pentaho-env.bat"

set OPT="-XX:MaxPermSize=256m" "-Dswing.useSystemFontSettings=false" "-Xms1024M" "-Xmx2048M"

REM START HITACHI VANTARA LICENSE
if not "%PENTAHO_INSTALLED_LICENSE_PATH%" == "" goto setLicenseParameter
goto skipToStartup

:setLicenseParameter
set OPT=%OPT% -Dpentaho.installed.licenses.file="%PENTAHO_INSTALLED_LICENSE_PATH%"

:skipToStartup
REM END HITACHI VANTARA LICENSE
"%_PENTAHO_JAVA%" %OPT% -jar "%~dp0launcher.jar" %* >> reportdesigner.log 2>&1