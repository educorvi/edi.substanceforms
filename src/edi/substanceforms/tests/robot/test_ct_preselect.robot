# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.substanceforms -t test_preselect.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.substanceforms.testing.EDI_SUBSTANCEFORMS_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/substanceforms/tests/robot/test_preselect.robot
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

Scenario: As a site administrator I can add a Preselect
  Given a logged-in site administrator
    and an add Tabelle form
   When I type 'My Preselect' into the title field
    and I submit the form
   Then a Preselect with the title 'My Preselect' has been created

Scenario: As a site administrator I can view a Preselect
  Given a logged-in site administrator
    and a Preselect 'My Preselect'
   When I go to the Preselect view
   Then I can see the Preselect title 'My Preselect'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Tabelle form
  Go To  ${PLONE_URL}/++add++Tabelle

a Preselect 'My Preselect'
  Create content  type=Tabelle  id=my-preselect  title=My Preselect

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Preselect view
  Go To  ${PLONE_URL}/my-preselect
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Preselect with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Preselect title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
