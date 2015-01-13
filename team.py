from flask import Blueprint, render_template, current_app, abort, g, \
    request, url_for
from galatea.tryton import tryton
from flask.ext.paginate import Pagination
from flask.ext.babel import gettext as _, lazy_gettext

team = Blueprint('team', __name__, template_folder='templates')

DISPLAY_MSG = lazy_gettext('Displaying <b>{start} - {end}</b> of <b>{total}</b>')

Team = tryton.pool.get('galatea.team')

GALATEA_WEBSITE = current_app.config.get('TRYTON_GALATEA_SITE')
LIMIT = current_app.config.get('TRYTON_PAGINATION_TEAM_LIMIT', 20)

TEAM_FIELD_NAMES = ['name', 'slug', 'avatar_path', 'description']

@team.route("/<slug>", endpoint="team")
@tryton.transaction()
def team_detail(lang, slug):
    '''Team detail'''
    teams = Team.search([
        ('slug', '=', slug),
        ('active', '=', True),
        ('websites', 'in', [GALATEA_WEBSITE]),
        ], limit=1)

    if not teams:
        abort(404)
    team, = teams

    breadcrumbs = [{
        'slug': url_for('.teams', lang=g.language),
        'name': _('Team'),
        }, {
        'slug': url_for('.team', lang=g.language, slug=team.slug),
        'name': team.name,
        }]

    return render_template('team.html',
            team=team,
            breadcrumbs=breadcrumbs,
            )

@team.route("/", endpoint="teams")
@tryton.transaction()
def teams(lang):
    '''Teams'''
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1

    domain = [
        ('active', '=', True),
        ('websites', 'in', [GALATEA_WEBSITE]),
        ]
    total = Team.search_count(domain)
    offset = (page-1)*LIMIT

    order = [('name', 'ASC')]
    teams = Team.search_read(domain, offset, LIMIT, order, TEAM_FIELD_NAMES)

    pagination = Pagination(page=page, total=total, per_page=LIMIT, display_msg=DISPLAY_MSG, bs_version='3')

    #breadcumbs
    breadcrumbs = [{
        'slug': url_for('.teams', lang=g.language),
        'name': _('Blog'),
        }]

    return render_template('teams.html',
            teams=teams,
            pagination=pagination,
            breadcrumbs=breadcrumbs,
            )
