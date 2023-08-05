'''
test en-zh
'''
# import sys
import pytest

from loguru import logger
# sys.path.insert(0, '..')

# from google_tr_async.google_tr_async import google_tr_async
from google_tr_async import google_tr_async


@pytest.mark.asyncio
async def test_0():
    ''' test 0'''
    text = \
        '''There is now some uncertainty about the future of Google News in Europe after the European Union finalized its controversial new copyright legislation.

        Google had previously showed how dramatically its search results could be affected, and warned that it may shut down the service in Europe …

        The EU Copyright Directive is well-intentioned, requiring tech giants to license the right to reproduce copyrighted material on their own websites. However, the legislation as originally proposed would have made it impossible for Google to display brief snippets and photos from news stories in its search results without paying the news sites.

        Google last month showed how its news search results would appear without photos and text excerpts, rendering the service all but useless. The company had previously said that its only option might be to shut down Google News in Europe.'''
    trtext = await google_tr_async(text)
    assert len(google_tr_async.dual) == 6
    assert len(trtext) > 200


@pytest.mark.asyncio
async def test_1():
    ''' test 1 zh2en'''
    text = '这是测试'
    trtext = await google_tr_async(text, to_lang='en')
    logger.debug('trtext: %s' % trtext)
    logger.debug('google_tr_async.dual: %s' % google_tr_async.dual)
    # assert len(google_tr_async.dual) == 6
    # assert google_tr_async.dual == 6
    # assert len(trtext) > 200
    assert trtext == 'This is a test'
