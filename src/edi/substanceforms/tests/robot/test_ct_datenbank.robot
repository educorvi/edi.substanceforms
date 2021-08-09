# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.substanceforms -t test_datenbank.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.substanceforms.testing.EDI_SUBSTANCEFORMS_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/substanceforms/tests/robot/test_datenbank.robot
#
# See the http://docs.plone.org for further details (search for robot
# framework).
#
# ============================================================================

*** Settings *****************************************************************

Resource  plone/app/robotframework/selenium.robot
Resource  plone/app/robotframework/keywords.robot

Library  Remote  ${PLONE_URL}/RobotRemote

Test Setup  Open test browser
Test Teardown  Close all browsers


*** Test Cases ***************************************************************

Scenario: As a site administrator I can add a Datenbank
  Given a logged-in site administrator
    and an add Datenbank form
   When I type 'My Datenbank' into the title field
    and I submit the form
   Then a Datenbank with the title 'My Datenbank' has been created

Scenario: As a site administrator I can view a Datenbank
  Given a logged-in site administrator
    and a Datenbank 'My Datenbank'
   When I go to the Datenbank view
   Then I can see the Datenbank title 'My Datenbank'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Datenbank form
  Go To  ${PLONE_URL}/++add++Datenbank

a Datenbank 'My Datenbank'
  Create content  type=Datenbank  id=my-datenbank  title=My Datenbank

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Datenbank view
  Go To  ${PLONE_URL}/my-datenbank
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Datenbank with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Datenbank title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
