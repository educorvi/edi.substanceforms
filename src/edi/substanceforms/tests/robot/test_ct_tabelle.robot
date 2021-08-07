# ============================================================================
# DEXTERITY ROBOT TESTS
# ============================================================================
#
# Run this robot test stand-alone:
#
#  $ bin/test -s edi.substanceforms -t test_tabelle.robot --all
#
# Run this robot test with robot server (which is faster):
#
# 1) Start robot server:
#
# $ bin/robot-server --reload-path src edi.substanceforms.testing.EDI_SUBSTANCEFORMS_ACCEPTANCE_TESTING
#
# 2) Run robot tests:
#
# $ bin/robot /src/edi/substanceforms/tests/robot/test_tabelle.robot
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

Scenario: As a site administrator I can add a Tabelle
  Given a logged-in site administrator
    and an add Datenbank form
   When I type 'My Tabelle' into the title field
    and I submit the form
   Then a Tabelle with the title 'My Tabelle' has been created

Scenario: As a site administrator I can view a Tabelle
  Given a logged-in site administrator
    and a Tabelle 'My Tabelle'
   When I go to the Tabelle view
   Then I can see the Tabelle title 'My Tabelle'


*** Keywords *****************************************************************

# --- Given ------------------------------------------------------------------

a logged-in site administrator
  Enable autologin as  Site Administrator

an add Datenbank form
  Go To  ${PLONE_URL}/++add++Datenbank

a Tabelle 'My Tabelle'
  Create content  type=Datenbank  id=my-tabelle  title=My Tabelle

# --- WHEN -------------------------------------------------------------------

I type '${title}' into the title field
  Input Text  name=form.widgets.IBasic.title  ${title}

I submit the form
  Click Button  Save

I go to the Tabelle view
  Go To  ${PLONE_URL}/my-tabelle
  Wait until page contains  Site Map


# --- THEN -------------------------------------------------------------------

a Tabelle with the title '${title}' has been created
  Wait until page contains  Site Map
  Page should contain  ${title}
  Page should contain  Item created

I can see the Tabelle title '${title}'
  Wait until page contains  Site Map
  Page should contain  ${title}
