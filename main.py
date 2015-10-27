import os
import cgi
import urllib
import datetime
import time
import jinja2
import webapp2

from google.appengine.ext import ndb

# validators


def valid_post(post):
    if post:
        return post


def valid_author(author):
    if author:
        return author

# Set up jinja environment

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader=jinja2.FileSystemLoader(template_dir),
                               autoescape=True)

# jinja rendering functions


class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

# This is the object that will represent our Post.


class Post(ndb.Model):
    """A main model for representing an individual post entry."""
    author = ndb.StringProperty(indexed=False)
    content = ndb.StringProperty(indexed=False)
    date = ndb.DateTimeProperty(auto_now_add=True)


class MainPage(Handler):
    def get(self):
        form_errors = self.request.get_all("error")

        # [START query]
        posts_query = Post.query(Post.date <=
                                 datetime.datetime.now()).order(-Post.date)
        # The function fetch() returns all posts that satisfy our query.
        # The function returns a list of post objects
        posts = posts_query.fetch()
        # [END query]

        # Render our template w/ jinja and pass in our comments
        self.render("stage_four.html", errors=form_errors, comments=posts)


class PostComment(webapp2.RequestHandler):
    def post(self):

        post = Post()

        # Get the content from our request parameters
        # as long as they pass validation
        # the comment is in the parameter 'content'
        # the author is in the parameter 'author'
        post.content = valid_post(self.request.get('content'))
        post.author = valid_author(self.request.get('author'))

        if not (post.content and post.author):
            input_error = '?'
            if not post.author:
                input_error += 'error=author&'
            if not post.content:
                input_error += 'error=content'
            self.redirect('/'+input_error)

        else:
            # Write it to the Google Database
            post.put()
            # if we take a tiny baby nap here, our entity should
            # have enough time to populate the database..
            time.sleep(.33)
            # and now we can redirect back to MainPage
            self.redirect('/')

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/comment', PostComment),
], debug=True)
