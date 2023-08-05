Changelog
=========


1.0a6 (2020-01-23)
------------------

- exclude Registration form from nav; add default new content and footer images; override footer and colophon templates
  [tkimnguyen]

1.0a5 (2020-01-22)
------------------

- add plonesite recipe to create the Sandia site automatically
  [tkimnguyen]


1.0a4 (2020-01-22)
------------------

- monkey patch plone.dexterity (#124)
  [tkimnguyen]


1.0a3 (2020-01-22)
------------------

- Rebuilt add-on starting with bobtemplates.plone:addon so it loads correctly in plonesite recipe
  [tkimnguyen]


1.0a1 (2020-01-15)
------------------

- updated to work with Plone 5.2 on Python 3.7
- add conference type, add base event-ish default view for conference, add collection behaviour to conference type, add object added event handler, add speakers folder, add talks folder, constrain addable types
- constrain types in Conference types, fix subfolder constrains
- manually create a template registration form; on conference create, copy the template registration form into it
- on installation, import template registration form into site root
- use bug fix branch of plone.dexterity to allow template registration form creation
- set email address in mailer adapter of copied registration form to event contact email address
- create on save handler to update registration form mail recipient_email if event contact email changes
- create uninstall profile
- show collection at bottom of Conference view
- add conference_listing_view (shows list of talks), make conference_view the default
- set default collection constraints to list presentations
- automatically include sandia.conferencetheme add-on
- move login link to footer
- hide search viewlet
- remove unneeded plone.tiles behavior in Conference type
- fix add-on name and URLs in setup.py
- change underlying name of add-on to sandia.conferencepolicy
- update README with new add-on name and info
  [tkimnguyen]

0.1 (2016, 2017, 2018)
----------------------

- deployed to 2018.ploneconf.org

- updates for 2017.ploneconf.org
  [sneridagh, tkimnguyen]

- Initial release for 2016.ploneconf.org.
  [alecpm, tkimnguyen]
