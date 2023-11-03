import random;

MIN_THREAD_ID = 1;
MAX_THREAD_ID = 100;

MIN_TAG_ID = 1;
MAX_TAG_ID = 100;

MIN_NUMBERS_OF_TAGS = 1;
MAX_NUMBERS_OF_TAGS = 10;

for threadId in range ( MIN_THREAD_ID, MAX_THREAD_ID + 1 ):
    numberOfTags = random.randrange ( MIN_NUMBERS_OF_TAGS, MAX_NUMBERS_OF_TAGS );
    tagIds = [ ];
    for i in range ( numberOfTags ):
        while ( True ):
            tagId = random.randrange ( MIN_TAG_ID, MAX_TAG_ID );
            if ( not ( tagId in tagIds ) ):
                tagIds.append ( tagId );
                break;

    # file = open ( path, mode );
    # file.read ( )/file.write ( )
    # file.close ( )

    with open ( "initialization.sql", "a" ) as outputFile:
        for tagId in tagIds:
            outputFile.write (
                f"INSERT INTO threadtag (threadId, tagId) VALUES ({threadId}, {tagId});\n"
            );
