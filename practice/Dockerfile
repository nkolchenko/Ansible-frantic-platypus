#v3 - ok
FROM jekyll/jekyll:latest
#
#   I wanted to include the assets I already had, hence the structure
#   otherwise there is NO need to re-build an image
#
#RUN mkdir /srv/jekyll-1
#RUN chmod 777 /srv/jekyll-1
#WORKDIR /srv/jekyll-1
#RUN jekyll new mysite
#WORKDIR /srv/jekyll-1/mysite
#COPY ./jekyll/mysite/* ./
#COPY ./jekyll/mysite/_posts ./jekyll/mysite/_site ./jekyll/mysite/404.html /srv/jekyll-1/mysite/
CMD jekyll serve
EXPOSE 4000


#Working!
#FROM jekyll/jekyll:3.8
#RUN mkdir /srv/jekyll-1
#RUN chmod 777 /srv/jekyll-1
#WORKDIR /srv/jekyll-1
#RUN jekyll new myblog
#WORKDIR /srv/jekyll-1/myblog
##RUN bundle exec jekyll serve
#CMD jekyll serve
#EXPOSE 4000