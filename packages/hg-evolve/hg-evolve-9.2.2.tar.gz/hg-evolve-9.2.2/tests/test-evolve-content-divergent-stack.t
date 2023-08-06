=================================================
Tests the resolution of content divergence: stack
=================================================

This file intend to cover case with stacks of divergent changesets

  $ cat >> $HGRCPATH <<EOF
  > [alias]
  > glog = log -GT "{rev}:{node|short} {desc|firstline}\n ({bookmarks}) [{branch}] {phase}"
  > [phases]
  > publish = False
  > [extensions]
  > rebase =
  > EOF
  $ echo "evolve=$(echo $(dirname $TESTDIR))/hgext3rd/evolve/" >> $HGRCPATH

Resolving content-divergence of a stack with same parents
---------------------------------------------------------

  $ hg init stacktest
  $ cd stacktest
  $ echo ".*\.orig" > .hgignore
  $ hg add .hgignore
  $ hg ci -m "added hgignore"
  $ for ch in a b c d; do echo foo > $ch; hg add $ch; hg ci -qm "added "$ch; done;

  $ hg glog
  @  4:c41c793e0ef1 added d
  |   () [default] draft
  o  3:ca1b80f7960a added c
  |   () [default] draft
  o  2:b1661037fa25 added b
  |   () [default] draft
  o  1:c7586e2a9264 added a
  |   () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ cd ..
  $ hg init stack2
  $ cd stack2
  $ hg pull ../stacktest
  pulling from ../stacktest
  requesting all changes
  adding changesets
  adding manifests
  adding file changes
  added 5 changesets with 5 changes to 5 files
  new changesets 8fa14d15e168:c41c793e0ef1 (5 drafts)
  (run 'hg update' to get a working copy)
  $ hg glog
  o  4:c41c793e0ef1 added d
  |   () [default] draft
  o  3:ca1b80f7960a added c
  |   () [default] draft
  o  2:b1661037fa25 added b
  |   () [default] draft
  o  1:c7586e2a9264 added a
  |   () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg up c7586e2a9264
  2 files updated, 0 files merged, 0 files removed, 0 files unresolved
  $ echo bar > a
  $ hg amend -m "watbar to a"
  3 new orphan changesets
  $ echo wat > a
  $ hg amend -m "watbar to a"
  $ hg evolve --all
  move:[2] added b
  atop:[6] watbar to a
  move:[3] added c
  move:[4] added d
  $ hg glog
  o  9:15c781f93cac added d
  |   () [default] draft
  o  8:9e5fb1d5b955 added c
  |   () [default] draft
  o  7:88516dccf68a added b
  |   () [default] draft
  @  6:82b74d5dc678 watbar to a
  |   () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ cd ../stacktest
  $ hg up .^^^
  0 files updated, 0 files merged, 3 files removed, 0 files unresolved
  $ echo wat > a
  $ hg amend -m "watbar to a"
  3 new orphan changesets
  $ hg evolve --all
  move:[2] added b
  atop:[5] watbar to a
  move:[3] added c
  move:[4] added d
  $ hg glog
  o  8:c72d2885eb51 added d
  |   () [default] draft
  o  7:3ce4be6d8e5e added c
  |   () [default] draft
  o  6:d5f148423c16 added b
  |   () [default] draft
  @  5:8e222f257bbf watbar to a
  |   () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg pull ../stack2
  pulling from ../stack2
  searching for changes
  adding changesets
  adding manifests
  adding file changes
  added 4 changesets with 0 changes to 4 files (+1 heads)
  5 new obsolescence markers
  8 new content-divergent changesets
  new changesets 82b74d5dc678:15c781f93cac (4 drafts)
  (run 'hg heads' to see heads, 'hg merge' to merge)

  $ hg glog
  *  12:15c781f93cac added d
  |   () [default] draft
  *  11:9e5fb1d5b955 added c
  |   () [default] draft
  *  10:88516dccf68a added b
  |   () [default] draft
  *  9:82b74d5dc678 watbar to a
  |   () [default] draft
  | *  8:c72d2885eb51 added d
  | |   () [default] draft
  | *  7:3ce4be6d8e5e added c
  | |   () [default] draft
  | *  6:d5f148423c16 added b
  | |   () [default] draft
  | @  5:8e222f257bbf watbar to a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg evolve --all --content-divergent
  merge:[5] watbar to a
  with: [9] watbar to a
  base: [1] added a
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  merge:[6] added b
  with: [10] added b
  base: [2] added b
  rebasing "divergent" content-divergent changeset d5f148423c16 on f66f262fff6c
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  merge:[7] added c
  with: [11] added c
  base: [3] added c
  rebasing "divergent" content-divergent changeset 3ce4be6d8e5e on eadfd9d70680
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  merge:[8] added d
  with: [12] added d
  base: [4] added d
  rebasing "divergent" content-divergent changeset c72d2885eb51 on b2cac10f3836
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  working directory is now at f66f262fff6c

  $ hg glog
  o  19:038fe7db3d88 added d
  |   () [default] draft
  o  17:b2cac10f3836 added c
  |   () [default] draft
  o  15:eadfd9d70680 added b
  |   () [default] draft
  @  13:f66f262fff6c watbar to a
  |   () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft
Resolving content-divergence of a stack with different parents
---------------------------------------------------------

  $ cd ..
  $ hg init stackrepo1
  $ cd stackrepo1
  $ echo ".*\.orig" > .hgignore
  $ hg add .hgignore
  $ hg ci -m "added hgignore"

  $ for ch in a b c d;
  > do echo foo > $ch;
  > hg add $ch;
  > hg ci -qm "added "$ch;
  > done;

  $ hg glog
  @  4:c41c793e0ef1 added d
  |   () [default] draft
  o  3:ca1b80f7960a added c
  |   () [default] draft
  o  2:b1661037fa25 added b
  |   () [default] draft
  o  1:c7586e2a9264 added a
  |   () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ cd ..
  $ hg init stackrepo2
  $ cd stackrepo2
  $ hg pull ../stackrepo1
  pulling from ../stackrepo1
  requesting all changes
  adding changesets
  adding manifests
  adding file changes
  added 5 changesets with 5 changes to 5 files
  new changesets 8fa14d15e168:c41c793e0ef1 (5 drafts)
  (run 'hg update' to get a working copy)

  $ hg glog
  o  4:c41c793e0ef1 added d
  |   () [default] draft
  o  3:ca1b80f7960a added c
  |   () [default] draft
  o  2:b1661037fa25 added b
  |   () [default] draft
  o  1:c7586e2a9264 added a
  |   () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg up 8fa14d15e168
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  $ echo newfile > newfile
  $ hg ci -Am "add newfile"
  adding newfile
  created new head
  $ hg rebase -s c7586e2a9264 -d .
  rebasing 1:c7586e2a9264 "added a"
  rebasing 2:b1661037fa25 "added b"
  rebasing 3:ca1b80f7960a "added c"
  rebasing 4:c41c793e0ef1 "added d"

  $ hg glog
  o  9:d45f050514c2 added d
  |   () [default] draft
  o  8:8ed612937375 added c
  |   () [default] draft
  o  7:6eb54b5af3fb added b
  |   () [default] draft
  o  6:c04ff147ef79 added a
  |   () [default] draft
  @  5:2228e3b74514 add newfile
  |   () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ cd ../stackrepo1
  $ hg up .^^^
  0 files updated, 0 files merged, 3 files removed, 0 files unresolved
  $ echo wat > a
  $ hg amend -m "watbar to a"
  3 new orphan changesets
  $ hg evolve --all
  move:[2] added b
  atop:[5] watbar to a
  move:[3] added c
  move:[4] added d

  $ hg glog
  o  8:c72d2885eb51 added d
  |   () [default] draft
  o  7:3ce4be6d8e5e added c
  |   () [default] draft
  o  6:d5f148423c16 added b
  |   () [default] draft
  @  5:8e222f257bbf watbar to a
  |   () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg pull ../stackrepo2
  pulling from ../stackrepo2
  searching for changes
  adding changesets
  adding manifests
  adding file changes
  added 5 changesets with 1 changes to 5 files (+1 heads)
  4 new obsolescence markers
  8 new content-divergent changesets
  new changesets 2228e3b74514:d45f050514c2 (5 drafts)
  (run 'hg heads' to see heads, 'hg merge' to merge)

  $ hg glog
  *  13:d45f050514c2 added d
  |   () [default] draft
  *  12:8ed612937375 added c
  |   () [default] draft
  *  11:6eb54b5af3fb added b
  |   () [default] draft
  *  10:c04ff147ef79 added a
  |   () [default] draft
  o  9:2228e3b74514 add newfile
  |   () [default] draft
  | *  8:c72d2885eb51 added d
  | |   () [default] draft
  | *  7:3ce4be6d8e5e added c
  | |   () [default] draft
  | *  6:d5f148423c16 added b
  | |   () [default] draft
  | @  5:8e222f257bbf watbar to a
  |/    () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft

  $ hg evolve --all --content-divergent
  merge:[10] added a
  with: [5] watbar to a
  base: [1] added a
  rebasing "other" content-divergent changeset 8e222f257bbf on 2228e3b74514
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  merge:[11] added b
  with: [6] added b
  base: [2] added b
  rebasing "divergent" content-divergent changeset 6eb54b5af3fb on 74fbf3e6a0b6
  rebasing "other" content-divergent changeset d5f148423c16 on 74fbf3e6a0b6
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  merge:[12] added c
  with: [7] added c
  base: [3] added c
  rebasing "divergent" content-divergent changeset 8ed612937375 on 4e29776e83a5
  rebasing "other" content-divergent changeset 3ce4be6d8e5e on 4e29776e83a5
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  merge:[13] added d
  with: [8] added d
  base: [4] added d
  rebasing "divergent" content-divergent changeset d45f050514c2 on 77126af93a25
  rebasing "other" content-divergent changeset c72d2885eb51 on 77126af93a25
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  working directory is now at 74fbf3e6a0b6

  $ hg glog
  o  24:c8f73c376a6e added d
  |   () [default] draft
  o  21:77126af93a25 added c
  |   () [default] draft
  o  18:4e29776e83a5 added b
  |   () [default] draft
  @  15:74fbf3e6a0b6 watbar to a
  |   () [default] draft
  o  9:2228e3b74514 add newfile
  |   () [default] draft
  o  0:8fa14d15e168 added hgignore
      () [default] draft
  $ cd ..

Make sure that content-divergent resolution doesn't undo a change (issue6203)
-----------------------------------------------------------------------------

  $ hg init issue6203
  $ cd issue6203
  $ echo a > a; hg add a; hg ci -m a
  $ echo 'b with typo' > b; hg add b; hg ci -m b
  $ echo c > c; hg add c; hg ci -m c

  $ hg prev
  0 files updated, 0 files merged, 1 files removed, 0 files unresolved
  [1] b
  $ echo 'b without typo' > b
  $ hg amend
  1 new orphan changesets
  $ hg evolve
  move:[2] c
  atop:[3] b

  $ hg up 0
  0 files updated, 0 files merged, 1 files removed, 0 files unresolved
  $ echo d > d; hg add d; hg ci -m d
  created new head
  $ hg rebase --hidden --config experimental.evolution.allowdivergence=True -s 1 -d 5
  rebasing 1:d420a663b65e "b"
  rebasing 2:49f182e7a6cc "c"
  4 new content-divergent changesets
  $ hg log -G -v --patch
  *  changeset:   7:ef4885dea3da
  |  tag:         tip
  |  user:        test
  |  date:        Thu Jan 01 00:00:00 1970 +0000
  |  instability: content-divergent
  |  files:       c
  |  description:
  |  c
  |
  |
  |  diff -r fe788ccf5416 -r ef4885dea3da c
  |  --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  |  +++ b/c	Thu Jan 01 00:00:00 1970 +0000
  |  @@ -0,0 +1,1 @@
  |  +c
  |
  *  changeset:   6:fe788ccf5416
  |  user:        test
  |  date:        Thu Jan 01 00:00:00 1970 +0000
  |  instability: content-divergent
  |  files:       b
  |  description:
  |  b
  |
  |
  |  diff -r 980f7dc84c29 -r fe788ccf5416 b
  |  --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  |  +++ b/b	Thu Jan 01 00:00:00 1970 +0000
  |  @@ -0,0 +1,1 @@
  |  +b with typo
  |
  @  changeset:   5:980f7dc84c29
  |  parent:      0:cb9a9f314b8b
  |  user:        test
  |  date:        Thu Jan 01 00:00:00 1970 +0000
  |  files:       d
  |  description:
  |  d
  |
  |
  |  diff -r cb9a9f314b8b -r 980f7dc84c29 d
  |  --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  |  +++ b/d	Thu Jan 01 00:00:00 1970 +0000
  |  @@ -0,0 +1,1 @@
  |  +d
  |
  | *  changeset:   4:fef59171875e
  | |  user:        test
  | |  date:        Thu Jan 01 00:00:00 1970 +0000
  | |  instability: content-divergent
  | |  files:       c
  | |  description:
  | |  c
  | |
  | |
  | |  diff -r 5b2d00df9c4e -r fef59171875e c
  | |  --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  | |  +++ b/c	Thu Jan 01 00:00:00 1970 +0000
  | |  @@ -0,0 +1,1 @@
  | |  +c
  | |
  | *  changeset:   3:5b2d00df9c4e
  |/   parent:      0:cb9a9f314b8b
  |    user:        test
  |    date:        Thu Jan 01 00:00:00 1970 +0000
  |    instability: content-divergent
  |    files:       b
  |    description:
  |    b
  |
  |
  |    diff -r cb9a9f314b8b -r 5b2d00df9c4e b
  |    --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  |    +++ b/b	Thu Jan 01 00:00:00 1970 +0000
  |    @@ -0,0 +1,1 @@
  |    +b without typo
  |
  o  changeset:   0:cb9a9f314b8b
     user:        test
     date:        Thu Jan 01 00:00:00 1970 +0000
     files:       a
     description:
     a
  
  
     diff -r 000000000000 -r cb9a9f314b8b a
     --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
     +++ b/a	Thu Jan 01 00:00:00 1970 +0000
     @@ -0,0 +1,1 @@
     +a
  

  $ hg evolve --content-divergent
  merge:[6] b
  with: [3] b
  base: [1] b
  rebasing "other" content-divergent changeset 5b2d00df9c4e on 980f7dc84c29
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  merge:[7] c
  with: [4] c
  base: [2] c
  rebasing "divergent" content-divergent changeset ef4885dea3da on 0999c349998d
  rebasing "other" content-divergent changeset fef59171875e on 0999c349998d
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved

Expected result:
Changeset with description "b" only adds file "b" with content "b without typo".
Changeset with description "c" only adds file "c" with content "c".

  $ hg glog -l2 -p
  o  12:4ca627f76da9 c
  |   () [default] draftdiff -r 0999c349998d -r 4ca627f76da9 c
  |  --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
  |  +++ b/c	Thu Jan 01 00:00:00 1970 +0000
  |  @@ -0,0 +1,1 @@
  |  +c
  |
  o  9:0999c349998d b
  |   () [default] draftdiff -r 980f7dc84c29 -r 0999c349998d b
  ~  --- /dev/null	Thu Jan 01 00:00:00 1970 +0000
     +++ b/b	Thu Jan 01 00:00:00 1970 +0000
     @@ -0,0 +1,1 @@
     +b without typo
  
  $ cd ..

Testing case when resolution parent is ambiguous (MultipleSuccessorsError)
--------------------------------------------------------------------------

  $ hg init multiplesuccs1
  $ cd multiplesuccs1
  $ echo base > base
  $ hg ci -Aqm "added base"
  $ echo foo > foo
  $ hg ci -Aqm "added foo"
  $ echo bar > bar; echo car > car
  $ hg ci -Aqm "added bar and car"
  $ echo dar > dar
  $ hg ci -Aqm "added dar"

  $ cd ..
  $ hg clone multiplesuccs1 multiplesuccs2
  updating to branch default
  5 files updated, 0 files merged, 0 files removed, 0 files unresolved
  $ cd multiplesuccs2
  $ hg up -r "desc('added foo')"
  0 files updated, 0 files merged, 3 files removed, 0 files unresolved
  $ echo newfoo > foo
  $ hg amend
  2 new orphan changesets
  $ hg evolve
  move:[2] added bar and car
  atop:[4] added foo
  move:[3] added dar

  $ cd ../multiplesuccs1
  $ hg up -r "desc('added base')"
  0 files updated, 0 files merged, 4 files removed, 0 files unresolved
  $ echo tuna > tuna
  $ hg ci -Aqm "added tuna"
  $ hg rebase -s "desc('added foo')" -d .
  rebasing 1:8da7bbaea4f7 "added foo"
  rebasing 2:7f4b97b13607 "added bar and car"
  rebasing 3:9f12b2fcb3de "added dar"

  $ cd ../multiplesuccs2
  $ hg pull
  pulling from $TESTTMP/multiplesuccs1
  searching for changes
  adding changesets
  adding manifests
  adding file changes
  added 4 changesets with 1 changes to 5 files (+1 heads)
  3 new obsolescence markers
  6 new content-divergent changesets
  new changesets 9703820a7d5b:9a1f460df8b5 (4 drafts)
  (run 'hg heads' to see heads, 'hg merge' to merge)
  $ hg glog
  *  10:9a1f460df8b5 added dar
  |   () [default] draft
  *  9:7dd5b9d42ef3 added bar and car
  |   () [default] draft
  *  8:afd8b2ea1b77 added foo
  |   () [default] draft
  o  7:9703820a7d5b added tuna
  |   () [default] draft
  | *  6:57a3f8edf065 added dar
  | |   () [default] draft
  | *  5:f4ed107810a7 added bar and car
  | |   () [default] draft
  | @  4:8a2d93492f59 added foo
  |/    () [default] draft
  o  0:bde1d2b6b5e5 added base
      () [default] draft

  $ hg evolve -r 4+5 --content-divergent
  merge:[8] added foo
  with: [4] added foo
  base: [1] added foo
  rebasing "other" content-divergent changeset 8a2d93492f59 on 9703820a7d5b
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  merge:[9] added bar and car
  with: [5] added bar and car
  base: [2] added bar and car
  rebasing "divergent" content-divergent changeset 7dd5b9d42ef3 on 8ef6ad88580d
  rebasing "other" content-divergent changeset f4ed107810a7 on 8ef6ad88580d
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  2 new orphan changesets
  working directory is now at 8ef6ad88580d

  $ hg glog
  o  15:09ba686a465e added bar and car
  |   () [default] draft
  @  12:8ef6ad88580d added foo
  |   () [default] draft
  | *  10:9a1f460df8b5 added dar
  | |   () [default] draft
  | x  9:7dd5b9d42ef3 added bar and car
  | |   () [default] draft
  | x  8:afd8b2ea1b77 added foo
  |/    () [default] draft
  o  7:9703820a7d5b added tuna
  |   () [default] draft
  | *  6:57a3f8edf065 added dar
  | |   () [default] draft
  | x  5:f4ed107810a7 added bar and car
  | |   () [default] draft
  | x  4:8a2d93492f59 added foo
  |/    () [default] draft
  o  0:bde1d2b6b5e5 added base
      () [default] draft

  $ echo bar > bar; hg ci -Aqm "added bar"
  $ echo car > car; hg ci -Aqm "added car"
  $ hg prune --split -s 16+17 -r 15
  1 changesets pruned

  $ hg evolve --content-divergent
  skipping 57a3f8edf065: have a different parent than 9a1f460df8b5 (not handled yet)
  | 57a3f8edf065, 9a1f460df8b5 are not based on the same changeset.
  | With the current state of its implementation, 
  | evolve does not work in that case.
  | rebase one of them next to the other and run 
  | this command again.
  | - either: hg rebase --dest 'p1(57a3f8edf065)' -r 9a1f460df8b5
  | - or:     hg rebase --dest 'p1(9a1f460df8b5)' -r 57a3f8edf065
