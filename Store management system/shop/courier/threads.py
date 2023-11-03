from flask import Blueprint, request;
from sqlalchemy import and_, or_;
from redis import Redis;
from applications.configuration import Configuration;

from applications.models import database, Thread, ThreadTag, Tag;

threadsBlueprint = Blueprint ( "threads", __name__ );


@threadsBlueprint.route ( "/", methods = ["GET"] )
def threads ( ):
    return str ( Thread.query.all ( ) );


@threadsBlueprint.route ( "/<title>", methods = ["GET"] )
def createThread ( title ):
    # thread = Thread ( title = title );
    # database.session.add ( thread );
    # database.session.commit ( );

    # return str ( Thread.query.all ( ) );

    with Redis ( host = Configuration.REDIS_HOST ) as redis:
        redis.rpush ( Configuration.REDIS_THREADS_LIST, title );

    return "Thread pending approval!";


@threadsBlueprint.route ( "/<threadId>/<tagId>", methods = ["GET"] )
def addTagToThread ( threadId, tagId ):
    threadTag = ThreadTag ( threadId = threadId, tagId = tagId );
    database.session.add ( threadTag );
    database.session.commit ( );

    return str ( Thread.query.all ( ) );


@threadsBlueprint.route ( "/withWordsInTitle", methods = ["GET"] )
def getThreadsWithWordsInTitle ( ):
    words = [item.strip ( ) for item in request.args["words"].split ( "," )];

    threads = Thread.query.filter (
            and_ (
                    *[Thread.title.like ( f"%{word}%" ) for word in words]
            )
    ).all ( );

    return str ( threads );

@threadsBlueprint.route ( "/withTags", methods = ["GET"] )
def getThreadsWithTags ( ):
    tags = [item.strip ( ) for item in request.args["tags"].split ( "," )];

    threads = Thread.query.join ( ThreadTag ).join ( Tag ).filter (
            or_ (
                    *[Tag.name == tag for tag in tags]
            )
    ).all ( );

    return str ( threads );
