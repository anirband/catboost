#include "zlib.h"

#include <library/unittest/registar.h>

#include "file.h"
#include <util/system/tempfile.h>

#define ZDATA "./zdata"

Y_UNIT_TEST_SUITE(TZLibTest) {
    static const TString data = "8s7d5vc6s5vc67sa4c65ascx6asd4xcv76adsfxv76s";
    static const TString data2 = "cn8wk2bd9vb3vdfif83g1ks94bfiovtwv";

    Y_UNIT_TEST(Compress) {
        TUnbufferedFileOutput o(ZDATA);
        TZLibCompress c(&o, ZLib::ZLib);

        c.Write(~data, +data);
        c.Finish();
        o.Finish();
    }

    Y_UNIT_TEST(Decompress) {
        TTempFile tmpFile(ZDATA);

        {
            TUnbufferedFileInput i(ZDATA);
            TZLibDecompress d(&i);

            UNIT_ASSERT_EQUAL(d.ReadLine(), data);
        }
    }

    Y_UNIT_TEST(DecompressTwoStreams) {
        // Check that Decompress(Compress(X) + Compress(Y)) == X + Y
        TTempFile tmpFile(ZDATA);
        {
            TUnbufferedFileOutput o(ZDATA);
            TZLibCompress c1(&o, ZLib::ZLib);
            c1.Write(~data, +data);
            c1.Finish();
            TZLibCompress c2(&o, ZLib::ZLib);
            c2.Write(~data2, +data2);
            c2.Finish();
            o.Finish();
        }
        {
            TUnbufferedFileInput i(ZDATA);
            TZLibDecompress d(&i);

            UNIT_ASSERT_EQUAL(d.ReadLine(), data + data2);
        }
    }

    Y_UNIT_TEST(DecompressFirstOfTwoStreams) {
        // Check that Decompress(Compress(X) + Compress(Y)) == X when single stream is allowed
        TTempFile tmpFile(ZDATA);
        {
            TUnbufferedFileOutput o(ZDATA);
            TZLibCompress c1(&o, ZLib::ZLib);
            c1.Write(~data, +data);
            c1.Finish();
            TZLibCompress c2(&o, ZLib::ZLib);
            c2.Write(~data2, +data2);
            c2.Finish();
            o.Finish();
        }
        {
            TUnbufferedFileInput i(ZDATA);
            TZLibDecompress d(&i);
            d.SetAllowMultipleStreams(false);

            UNIT_ASSERT_EQUAL(d.ReadLine(), data);
        }
    }
}
