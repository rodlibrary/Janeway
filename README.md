![Janeway Logo](https://www.openlibhums.org/media/press/Janeway_RGB_Keyline_Logo_Black.png "Janeway")

# Rod Library Janeway

This repository is Rod Library's copy of [Janeway](https://github.com/openlibhums/janeway), the open source publishing platform for journals, preprints, conference proceedings and books. Janeway is developed and maintained by the Open Library of Humanities, part of Birkbeck, University of London.

Rod Library's version adds the [library.uni.edu](https://library.uni.edu/) look to Janeway's public pages:

- `src/static/common/css/rodlibrary.css`: UNI colours, fonts, header, link, button and footer styles
- `src/templates/common/elements/rodlibrary_footer.html`: the Rod Library and UNI footer
- `src/static/common/img/UNI-site-logo.png`: the UNI footer logo
- `docs/mockups/rodlibrary/`: [screenshots of every public page](docs/mockups/rodlibrary/README.md) in each theme

## Contents

- [How Janeway is organised](#how-janeway-is-organised)
- [Guide for administrators](#guide-for-administrators)
- [Guide for editors](#guide-for-editors)
- [Guide for submitters (authors)](#guide-for-submitters-authors)
- [Guide for reviewers](#guide-for-reviewers)
- [Getting help](#getting-help)
- [Developer information](#developer-information)

---

## How Janeway is organised

**Press and journals.** A Janeway site has one *press* (Rod Library Publishing) that hosts one or more *journals*. Each journal has its own website, settings, editorial team and workflow.

**Public site and back office.** Readers see each journal's public website. Staff work in the back office, which you reach by logging in and opening the **Dashboard**.

**Addresses.** Each journal has a short code, which appears in its web addresses. In this guide, `<site>` means the Janeway address and `<journal>` means the journal's code. For example, a journal with code `ijs` has its dashboard at `https://<site>/ijs/dashboard/`. If a journal has been given its own domain name instead, leave out the `/<journal>` part.

**Roles.** What each person can see and do depends on the roles they hold in a journal. One account can have different roles in different journals.

| Role | What they do |
|---|---|
| Staff / press administrator | Manages the whole site: creates journals and sets press-wide options |
| Journal Manager (Editor with manager access) | Configures a journal's settings, content, users and workflow |
| Editor | Oversees every submission in the journal and makes publication decisions |
| Section Editor | Handles the submissions they are assigned |
| Reviewer | Peer reviews submissions when invited |
| Copyeditor | Copyedits accepted articles |
| Production Manager / Typesetter | Prepares publication files (galleys) such as PDF, HTML and XML |
| Proofing Manager / Proofreader | Checks galleys before publication |
| Author | Submits work and responds to editors |

---

## Guide for administrators

Administrators are Rod Library staff who run the platform and set up journals.

### First-time setup

1. Install Janeway on the server. Follow [Installing Janeway](https://janeway.readthedocs.io/en/latest/dev/installation.html), or see [Developer information](#developer-information) to run it with Docker.
2. From `src/`, run `python3 manage.py install_janeway`. It asks for the press name, domain and contact email, and for details of the first journal.
3. Create your own administrator account with `python3 manage.py createsuperuser`.
4. Log in at `https://<site>/login/`.

### Press settings

The press manager is at `https://<site>/manager/` (staff accounts only). From there:

- **Edit Press** (`https://<site>/manager/press/`) sets the press name, contact details, logo and press theme (`OLH`, `clean` or `material`).
- **Journals** lists every journal, with links to each journal's settings.
- **Home Page** settings for the press choose which blocks appear on the press homepage. The **Journals** block has its own settings for choosing the featured journals.

### Creating a journal

1. In the press manager (`https://<site>/manager/`), choose **Add New Journal**. Give it a name and a short code; the code becomes part of its web addresses.
2. Choose **Edit Settings** next to the journal, or open its **Manager** page (`https://<site>/<journal>/manager/`) and work through the sections below.

### Configuring a journal

All of these options are on the journal's **Manager** page.

| Section | Options | What to set |
|---|---|---|
| Journal Settings | **General** | Name, ISSN, description, contact details, privacy policy URL and **theme** |
| Journal Settings | **Images** | Header logo, favicon and default cover image |
| Journal Settings | **Home Page** | Which blocks appear on the homepage (About, Current Issue, News, Featured Articles…) and in what order |
| Journal Settings | **Styling** | Display options for the theme |
| Review | **Review Settings**, **Review Forms** | Review type (for example double-blind), deadlines and the questions reviewers answer |
| Submission | **Submission Settings**, **Submission Fields Configurator** | Submission checklist, copyright statement and which fields authors fill in |
| Workflow | **Workflow** (left-hand menu) | Which stages articles pass through, and in what order (review, copyediting, production, proofing) |
| Content | **Content Manager**, **Submission Page Items**, **Editorial Team**, **Journal Contacts** | Pages such as About and Author Guidelines, the editorial board and contacts |
| News | **News Manager** | Announcements and calls for papers |
| Articles & Issues | **Sections (Article Types)**, **Issue Manager**, **Licence Manager** | Article types, issues and licences (for example CC BY 4.0) |
| Identifiers | **Crossref Settings**, **DOI Manager** | DOI prefix and Crossref deposit credentials |
| Users & Roles | **Enrol Users**, **Enrolled Users**, **Roles** | Accounts and the roles they hold |
| Emails | **Email Templates** | Wording of the emails Janeway sends |

### Applying the Rod Library look

The Rod Library styles and footer work with all three themes. To finish setting up a journal's look:

1. **Choose a theme.** Set it in **Manager → General → Journal theme**. The [mockups](docs/mockups/rodlibrary/README.md) show each theme side by side.
2. **Upload logos.** Add the journal's header logo and cover image in **Manager → Images**, and the press logo in the press manager's **Edit Press** page. Until you do, Janeway's default logo appears.
3. **Footer colours.** The colours are three settings at the start of the footer section of `src/static/common/css/rodlibrary.css`:
   ```css
   .uni-footer {
       --uni-footer-bg: #2e1a47;   /* background */
       --uni-footer-text: #ffffff; /* text */
       --uni-footer-link: #ffb500; /* links */
   ```
4. **Footer content.** Edit the addresses and links in `src/templates/common/elements/rodlibrary_footer.html`.
5. **Fonts.** library.uni.edu uses Proxima Nova and Blacker Pro from Adobe Fonts. To use them, add UNI's Adobe Fonts kit `<link>` to each theme's `src/themes/<theme>/templates/core/base.html`. Without it, similar standard fonts are used.
6. **Per-journal changes.** For a change that applies to one journal only, use the journal's own override stylesheet. It loads after `rodlibrary.css`, so its rules take priority.

After changing static files on the server, run `python3 manage.py collectstatic` and restart the web server.

### Managing users

- **Add an account:** **Manager → Enrol Users** to give a role to someone who already has an account, or **Manager → Add user** (`/<journal>/manager/user/add/`) to create a new account.
- **Change roles:** **Manager → Enrolled Users**, then edit the person's roles.
- **People can register themselves** at `/<journal>/register/step/1/`. New accounts start with the Author role only.

### Routine maintenance

- **Back up** the database and the `files/` and `media/` folders regularly.
- **Run the scheduled tasks** (`python3 manage.py ...` cron jobs for reminders and DOI deposits). See **Manager → Cache, Cron & Emails** and the [Janeway documentation](https://janeway.readthedocs.io/).
- **Clear the cache** with **Manager → Clear Cache** if a settings change doesn't show up.

---

## Guide for editors

Editors and Section Editors move submissions from arrival to publication. Most of your work happens in the back office: log in, then open **Dashboard** (`/<journal>/dashboard/`).

### Your workspace

- **Dashboard** lists tasks assigned to you, grouped by stage.
- **Kanban** shows every active submission as a card in its current stage.
- **Search Submissions** finds any article by title, author or ID.
- The **Workflow** menu has one page per stage: Unassigned, Review, Copyediting, Production, Proofing and Pre Publication.

### Typical workflow

1. **Unassigned.** New submissions arrive here. Open one, check it fits the journal, then **assign an editor** (yourself or a Section Editor). You can also **reject** it without review at this point.
2. **Review.**
   - Open the review round and **add reviewers**. You can choose existing accounts or add a new reviewer by email.
   - Set a due date and send the invitation. Reviewers get an email with a link.
   - Track who has accepted, declined or completed. Send reminders, or withdraw an invitation, from the review page.
   - Once you have enough reviews, choose **Make a Decision**: **Accept**, **Decline** or **Request revisions**. When you request revisions, the author is asked to upload a new version, and you can start a new review round after it arrives.
3. **Copyediting.** Assign a copyeditor. When the copyedited files come back, send them to the author for review if needed, then complete the stage.
4. **Production / Typesetting.** Assign a typesetter or upload the publication files (galleys) yourself. Most journals provide at least a PDF galley.
5. **Proofing.** Send galleys to proofreaders and to the author. Corrections go back to the typesetter.
6. **Pre Publication.** Check the article's metadata, then set the licence, publication date, issue and DOI. Press **Publish**, or schedule it for a future date.

At the end of each stage, use the stage's **Complete** button (for example **Complete Copyediting**) or **Move to Next** to pass the article on.

### Issues

- Create issues and add articles to them in **Back Content → Issue Manager** (`/<journal>/manage/issues/`).
- Set the **current issue** there. It is what the homepage's Current Issue block shows.
- **Publication Schedule** shows articles that are due to be published.

### Emails

Janeway emails people at each step: invitations, decisions, reminders. You can edit a message before it goes out. Journal Managers can change the standard wording in **Manager → Email Templates**.

---

## Guide for submitters (authors)

### Before you start

Read the journal's **Submissions** page (in the journal's menu). It explains the journal's scope, formatting requirements and licence.

### Create an account

1. On the journal's site, choose **Register**.
2. Fill in your details and confirm your email address using the link Janeway sends you.
3. Optionally, link your ORCID iD in your **Profile**.

### Submit an article

Choose **Start Submission**, or go to `/<journal>/submit/start/`. The submission form has these steps:

1. **Agreement.** Confirm the submission checklist and the copyright and licence terms.
2. **Article information.** Enter the title, abstract and keywords, and choose the section (article type) and language.
3. **Authors.** Add every co-author in the order they should appear, and choose the corresponding author. Include affiliations, and ORCID iDs if you have them.
4. **Files.** Upload your manuscript. If the journal uses blind review, remove your name from the file. Add any figures or data files as supplementary files.
5. **Funding.** List any funders and grant numbers.
6. **Review.** Check everything and choose **Submit**.

If you need to stop partway, your draft is saved. Return to it from **Dashboard → Submissions** (`/<journal>/submit/submissions/`).

### After you submit

- Your **Dashboard** shows each submission and its current stage.
- Janeway emails you when the editor makes a decision or needs something from you.
- **If revisions are requested:** open the revision request from the email link or your Dashboard. Upload a revised manuscript and explain your changes in the response box.
- **Copyediting and proofs:** you may be asked to approve copyedits or check proofs. Use the link in the email, make your comments and submit them by the deadline.
- When your article is published, it appears on the journal's website and you are notified.

---

## Guide for reviewers

1. **Respond to the invitation.** You'll receive an email invitation with a link. Accept or decline it. If the review is blind, you may not need to log in.
2. **Read the submission.** Download the manuscript from the review page.
3. **Write your review.** Complete the review form, give a recommendation and upload any annotated files. Submit by the due date shown.
4. **Find past reviews.** Your past and current reviews are listed under **Review Requests** on your Dashboard (`/<journal>/review/requests/`).

---

## Getting help

- **Using a Rod Library journal:** contact the journal's editorial team (see its **Contact** page) or [Rod Library](https://library.uni.edu/about-us/contact-us), (319) 273-2838.
- **Janeway documentation:** [janeway.readthedocs.io](https://janeway.readthedocs.io/), including the [user guides](https://janeway.readthedocs.io/en/latest/).
- **Janeway community and issue tracker:** [github.com/openlibhums/janeway](https://github.com/openlibhums/janeway/issues).

---

## Developer information

### Technology
Janeway is written in Python (3.10+) and utilises the Django framework (4.2).

### Installation instructions
Developer installation [instructions are available in our documentation site](https://janeway.readthedocs.io/en/latest/dev/installation.html).

A guide for installing on the live environment with [apache and mod_wsgi](https://github.com/openlibhums/janeway/wiki/Janeway%2C-Apache-and-WSGI) is also available.

### Running Janeway with docker
Janeway's development server can be run within a docker container, avoiding the need to install and run its dependencies from your machine. A docker compose file as well as a Makefile can be found at the root of the project wrapping the most common operations.
Docker is compatible with multiple architectures and Operating systems, if you need help installing docker, have a look at the [docker documentation](https://docs.docker.com/install/).

Simarly to the native installation, Janeway can be installed in a docker environment by running ``make install`` and following the installation steps described [above](https://github.com/openlibhums/janeway/wiki/Installation). As a result, a database volume will be populated under janeway/db/postgres-data
Once installation is completed, just type ``make janeway`` to run janeway with a postgres backend (default behaviour).

If a change to the dependencies for Janeway is required, the Janeway container can be re-created with ``make rebuild``. The database volume will be preserved.

In order to run a different RDBMS, the environment variable ``DB_VENDOR`` can be set to one of ``postgres``, ``mysql`` or ``sqlite``. e.g: ``DB_VENDOR=mysql make install && make``

Uninstalling Janeway is as simple as running ``make uninstall`` which will delete all docker related containers as well as wipe the database volume.

### Updating from upstream Janeway
This repository started from a snapshot of [openlibhums/janeway](https://github.com/openlibhums/janeway) at commit `7492522`, without the project's earlier history. To bring in a newer upstream release, apply the upstream changes since that commit:

```bash
git remote add upstream https://github.com/openlibhums/janeway.git
git fetch upstream
git checkout -b update-janeway
git diff 7492522 upstream/master | git apply --3way
```

Resolve any conflicts, which are most likely in the theme `base.html` files, then open a pull request. Use the newest upstream commit you merged as the starting point next time.

### Major Releases
All upstream releases are listed on the [releases](https://github.com/openlibhums/janeway/releases) page.

### Geolocation
Janeway includes GeoLite2 data created by MaxMind, available from [https://www.maxmind.com](https://www.maxmind.com)
