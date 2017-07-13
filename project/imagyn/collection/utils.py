import binascii

# Use these as filters for websites that return a real image with status code 200
# when they actually don't have an image
binary_images = {
    'flickr_notavailable': {
        'size': (500, 374),
        'raster': binascii.a2b_hex(""" 
            8950 4e47 0d0a 1a0a 0000 000d 4948 4452 0000 01f4 0000 0176 0800 0000 00bd c535 
            8500 0007 ca49 4441 5478 01ec d96d ebd2 501c c6f1 fffb 7f29 67e1 296f 420e 6692 
            e2cd 0a94 aca8 1945 66a9 336c d8b4 3a6e feba daa6 abe7 ff27 1eaf 2f78 cd6d 0f3f 
            3006 bbdb b29b eb6e 2bec c622 3ad1 19d1 19d1 19d1 19d1 19d1 19d1 d97d 17f5 b4f2 
            46f2 cc98 b644 e3f1 7829 655f 8c31 9f88 ee5c 7bad d050 ea4a 6959 e0ef 2b29 fb88 
            f3c0 3974 3685 6b6d 3023 fa2d d585 eb4e 2447 ff15 8661 ec38 3ab3 b60d 576b 8f39 
            7a6a ad4d e46f bbd5 7a77 414f 70f9 98c6 71fc 53a2 c586 e857 9e2a eafd f778 4fdf 
            5415 6a14 e849 1387 c577 4cab 8b71 119d e8b6 a5b2 aa05 fa04 3b11 a067 69a2 5f79 
            beff 108e be1f fc8b fe1c ebf5 5f0e 3b39 7a88 7992 5ed0 eb44 bffa 4cf1 c02e d17f 
            7bd8 252e 9d32 f4d7 b8f3 e820 39ba 9ead bf3a 884e f415 a653 bebd 57f0 5b49 81fe 
            c1cd b777 a2cf 317e 89ae f19b 9fd1 0f6e a213 7d83 699e 2ee8 538d 3be7 c7bb 25ba 
            9be8 a9c6 be38 8aec 33f4 e02d a6e3 363a d125 50a8 d27a ac92 0c3d 6d60 dfb9 8d4e 
            7499 a83c 9ba1 cb67 ec83 c81d 7436 30c6 e090 7f5a 5de3 e43d 4ebe 8d6a caab f692 
            e2d3 6a1f 87d1 8fa7 e80f 3b77 b3da 3610 0560 f4fd 5fe5 9228 f487 2656 f0c2 097a 
            096f da85 1f20 3fc5 916c 8c1a 7217 85c9 4e85 8266 ceb7 1a06 b43a 2086 e132 e7a6 
            d105 1dba a00b baa0 0bba a00b baa0 0bba a00b baa0 0bba a00b baa0 0b3a 7441 1774 
            4117 7441 1774 4117 7441 1774 4117 7441 1774 4117 74e8 822e e882 2ee8 822e e882 
            2ee8 822e e882 2ee8 822e e882 2ee8 d005 5dd0 055d d005 7d95 4117 7441 1774 4117 
            7441 1774 4117 7441 1774 4117 7441 1774 4187 2ee8 822e e882 2ee8 822e e882 2ee8 
            822e e882 2ee8 822e e882 0e5d d005 5dd0 055d d005 5dd0 055d d005 5dd0 055d d005 
            5dd0 051d baa0 0bba a00b baa0 0bba a00b baa0 0bba a00b baa0 0bba a00b fa65 bfed 
            baed fe02 bd9d 9ebe c547 dd33 f456 3a5e c797 c3e9 74b8 8eeb 37e8 6d34 7e8d abd7 
            f9bd df57 f17d 82de 42e3 5dc4 cf5c fe8a b89f a0b7 611e a75c 9f23 d5a1 576f 7e77 
            f517 bdeb 531d 7ae5 e6e3 360e f347 87d8 4ea9 0ebd 72f3 791f b7a7 f9bd d36d ece7 
            5487 5eb9 f97c e9e3 c7e1 7c3e dcc6 e632 a73a f4ba cddf 3bf6 f151 7f9c e72a d5a1 
            17e6 790d 7bdf 75f7 790d 5bb1 3af4 342f 6a4e 3dd1 9957 a70e bd30 a79e e8cc 537d 
            077d fdbd 0e37 b1b0 9be1 15fa 1a7b 49f2 a5ec 2fd0 57d8 100f 6ff3 c2de 1e62 80be 
            c26e 22cd 97a9 4707 7d85 45fc b7af a143 870e 1d3a 74e8 d0a1 4387 0e1d 3af4 0541 
            7fde 8df3 a7c6 dd53 c5e8 d077 d17f 521f fbd8 558c 0e7d ec53 bddc aa18 1dfa 67e2 
            2937 2a46 879e eaa5 79d5 e8d0 0bf5 34af 1a1d 7aa1 9ee6 f5a3 434f f5c2 bc72 74e8 
            a95e 9857 8e0e 3dd5 d3bc 0d74 e8a9 bed9 a479 2be8 d0e7 7113 b119 e796 d0a1 4fcd 
            a143 9f5a fbbd 43cf 73fb d8d2 410e fa94 dca9 5e33 3af4 d2bc 50af 101d 7a69 5ea8 
            5788 0ebd 342f d42b 4487 5e9a 17ea 15a2 432f cd0b f59a d1a1 4f0d 8c4b 4137 1809 
            fda9 fa11 68e8 cb82 feef 4187 0e1d 3a74 e8d0 a143 870e 1d3a 74e8 1e0f 843e c4e3 
            62f5 e363 0cd0 3d08 0c7d 1dea 4317 0beb 8617 4f7f 0bba a00b baa0 0bba a00b baa0 
            0bba a00b baa0 0bba a043 1774 4117 7441 1774 4117 7441 17f4 3fec 98a1 aff4 380c 
            c4ff ece1 c6c1 c5a6 a181 a166 8581 8566 8161 6673 df97 b6bb 014f 4fba b7f7 a403 
            1db0 9193 19bb d24f a9b4 7dc9 4f31 3c66 1d83 5fa8 777e ab11 fc5e c3f9 a146 ac4d 
            86ff bcef 031d a7e8 f059 67e1 1752 2557 b991 ab24 f37b 19f8 a124 af4d 0c9f f47d 
            6efa 8edd fd05 bd1f 5f43 ff9e e1d1 7f1d fad1 1fe8 ff9d 4edc 8e63 570b 3625 8fac 
            7bcc b35a 8f5c 3aa9 ea25 4f5b d13d d812 b433 762d cecb 47ee 9a1b a7b4 b55c 0657 
            83e1 5576 f539 89bd 686b ca99 3ce6 becd 0631 3b85 1e24 f34e 2f5a c71c 6120 479d 
            4d0c bdfc 0d19 eefc 4ff4 404f b5a0 d240 47b6 ad9c f844 2dc9 3857 0477 6493 14ae 
            b011 492c 633f 7d4a 4335 39a9 434a 15e5 6a30 dce5 35c9 3824 5916 9045 aca2 d121 
            dbcc e764 8a46 55f2 8077 942a 698e 984d d412 060d 9b29 0eda 3bff 133d 379d dc94 
            061a 0619 27cc 8d0c a973 3de0 2185 1c30 1a78 da8a c405 5db7 b842 4425 2bb8 1aec 
            5dde 93aa 8c69 eb70 7217 3a76 4e75 cef3 86c1 9266 79c0 4fe8 b38a f900 319f cede 
            f91f e881 eef7 6d1a 095b bda0 eb45 54a7 e3b4 4ed7 5ce6 e6e5 3b04 7a51 8391 86d5 
            b096 f7a4 591b 6850 d5ed dc9f 6a82 b229 432c 6467 2852 7d43 af10 9bd0 6778 cdf3 
            033d d019 4795 ed0d 7dcb 37f4 8e46 32e5 e9ca 8964 43bf 7da3 15d4 05fa 6a58 cb7b 
            52de cefd 1d87 ff51 dcd0 078c 2329 59d2 79d9 07ed 05bd c1e9 37f4 2a6b 9e1f e881 
            def7 6095 13ba 3877 b41b 3a35 7556 380d 118e ca9e 9417 f476 905b 5ea1 2f86 b5bc 
            2735 18fb 060e 29c1 63f9 ff70 bdfe d991 3299 b7f5 f5be 2318 13fa 4e97 427b e73f 
            d103 bd09 8076 c2dc 36a0 f005 7d28 203b e940 e52e 808e 1b7a 0520 7d85 be18 d6f2 
            9ec4 02a4 0cf2 1040 da0b 3a0b 5493 92dc 7090 5d92 ea0b 7a6c a279 422f c016 b477 
            fe5f e881 1e1e f76f ef1c 4eb2 7bf0 86d9 07e7 c1e5 1b7e 86e6 e263 fd62 e74e f2de 
            1eab 6129 df93 18c3 5984 7772 eedf e6de dfb3 7c84 c7fb d93a 7d70 38c7 db32 f30f 
            f4cf 7543 ff35 b954 2b30 fecf f440 af95 bfa7 965f 9f73 fe69 8f0e 0400 0000 1806 
            f95b dfe3 2b85 a423 1de9 4847 3ad2 918e 74a4 231d e948 473a d291 2e1d e948 473a 
            d291 8e74 a423 1de9 4847 3ad2 918e 74a4 235d 3ad2 918e 74a4 231d e948 473a d291 
            8e74 a423 1de9 4847 fa1f e948 473a d2a5 231d e948 473a d291 8e74 a423 1de9 4847 
            3ad2 918e 74a4 4b47 3ad2 918e 74a4 231d e948 473a d291 8e74 a423 1de9 4897 8e74 
            a423 1de9 4847 3ad2 918e 74a4 231d e948 473a d291 2e1d e948 473a d291 8e74 a423 
            1de9 4847 3ad2 918e 74a4 235d 3a39 0302 feb5 f0bf 5860 7e00 0000 0049 454e 44ae 
            4260 82""".replace(' ', '').replace('\n', '').replace('\t', '')
        )
    }
}
