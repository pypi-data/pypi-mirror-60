'''
google translate for free

'''
# pylint: disable=line-too-long, broad-except

from typing import Union, Dict

import sys
import asyncio

import js2py  # type: ignore

import httpx  # type: ignore

from loguru import logger
# import pytest

URL = 'http://translate.google.cn/translate_a/single'

TL = \
    """function RL(a, b) {
        var t = "a";
        var Yb = "+";
        for (var c = 0; c < b.length - 2; c += 3) {
            var d = b.charAt(c + 2),
            d = d >= t ? d.charCodeAt(0) - 87 : Number(d),
            d = b.charAt(c + 1) == Yb ? a >>> d: a << d;
            a = b.charAt(c) == Yb ? a + d & 4294967295 : a ^ d
        }
        return a
    }
        function TL(a) {
        var k = "";
        var b = 406644;
        var b1 = 3293161072;

        var jd = ".";
        var $b = "+-a^+6";
        var Zb = "+-3^+b+-f";

        for (var e = [], f = 0, g = 0; g < a.length; g++) {
            var m = a.charCodeAt(g);
            128 > m ? e[f++] = m : (2048 > m ? e[f++] = m >> 6 | 192 : (55296 == (m & 64512) && g + 1 < a.length && 56320 == (a.charCodeAt(g + 1) & 64512) ? (m = 65536 + ((m & 1023) << 10) + (a.charCodeAt(++g) & 1023),
            e[f++] = m >> 18 | 240,
            e[f++] = m >> 12 & 63 | 128) : e[f++] = m >> 12 | 224,
            e[f++] = m >> 6 & 63 | 128),
            e[f++] = m & 63 | 128)
        }
        a = b;
        for (f = 0; f < e.length; f++) a += e[f],
        a = RL(a, $b);
        a = RL(a, Zb);
        a ^= b1 || 0;
        0 > a && (a = (a & 2147483647) + 2147483648);
        a %= 1E6;
        return a.toString() + jd + (a ^ b)
    };"""

GEN_TOKEN = js2py.eval_js(TL)

HEADERS = {
    'User-Agent':
    'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:23.0) Gecko/20100101 Firefox/23.0'
}  # type: Dict[str, str]


async def google_tr_async(  # pylint: disable=too-many-arguments, too-many-locals, too-many-branches
        content: str,
        from_lang: str = 'auto',
        to_lang: str = 'zh-CN',
        proxy: Union[str, None] = None,
        timeout: float = 4,
        verify: bool = False,
        connect_timeout: float = 8.0,
        headers: Union[dict, None] = None,
        debug: bool = False,
):
    ''' google_tr_async '''

    if not debug:
        logger.remove()
        logger.add(sys.stderr, level="INFO")

    if len(content) > 4891:  # pragma: no cover
        logger.warning(' input longer than 4891, trimming to 4891...')
        content = content[:4891]

    if headers is None:
        headers = HEADERS

    req = httpx.models.Request('GET', URL)

    timeo = httpx.Timeout(timeout, connect_timeout=connect_timeout)

    token = GEN_TOKEN(content)
    data = dict(
        client="t",
        sl=from_lang,
        tl=to_lang,
        hl=to_lang,
        dt=[
            "at",
            "bd",
            "ex",
            "ld",
            "md",
            "qca",
            "rw",
            "rm",
            "ss",
            "t",
        ],
        ie="UTF-8",
        oe="UTF-8",
        clearbtn=1,
        otf=1,
        pc=1,
        srcrom=0,
        ssel=0,
        tsel=0,
        kc=2,
        tk=token,
        q=content,
    )

    # timeout exception
    try:
        async with httpx.AsyncClient(
                proxies=proxy,
                timeout=timeo,
                trust_env=False,
                headers=headers,
                verify=verify,
        ) as client:
            try:
                # resp = loop.run_until_complete(client.get(*args))
                # resp = await client.get(url)
                resp = await client.get(URL, params=data)
                resp.raise_for_status()
            except Exception as exc:  # pragma: no cover
                logger.error(exc)
                resp = httpx.Response(
                    status_code=499,
                    request=req,
                    content=str(exc).encode(),
                )

    except Exception as exc:  # pragma: no cover
        logger.error('timeout: %s' % exc)
        resp = httpx.Response(
            status_code=499,
            request=req,
            content=str(exc).encode(),
        )
    finally:
        logger.debug('resp: %s' % resp.text[:10])

    if debug:
        google_tr_async.resp = resp

    try:
        jdata = resp.json()
    except Exception as exc:  # pragma: no cover
        jdata = [{'error': str(exc)}]

    # google_tr_async.json = jdata

    try:
        res = [elm for elm in jdata[0] if elm[0] or elm[1]]
    except Exception as exc:  # pragma: no cover
        res = [str(exc)]

    if to_lang in ['zh-CN', 'zh']:
        _ = ''.join([str(elm[0]) for elm in res])
    else:
        _ = ' '.join([str(elm[0]) for elm in res])

    if debug:
        return _, proxy
    return _


def main():  # pragma: no cover
    ''' main '''
    from random import randint

    # fetch English input if any
    args = sys.argv[1:]
    if args:
        content = ' '.join(args)
    else:
        content, *args = ['test ' + str(randint(1, 10000)), 'en', 'zh']

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    task = loop.create_task(google_tr_async(content, *args))

    print(loop.run_until_complete(task))


if __name__ == '__main__':  # pragma: no cover
    main()
