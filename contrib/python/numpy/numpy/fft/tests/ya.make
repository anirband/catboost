PROGRAM()



NO_LINT()
NO_CHECK_IMPORTS()

PEERDIR(
    contrib/libs/nose/runner
    contrib/python/numpy
)

TEST_SRCS(
    test_fftpack.py
    test_helper.py
)

END()
