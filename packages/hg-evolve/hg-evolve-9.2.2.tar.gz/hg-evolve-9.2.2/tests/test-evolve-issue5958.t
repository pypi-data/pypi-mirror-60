Content divergence and trying to relocate a node on top of itself (issue5958)
https://bz.mercurial-scm.org/show_bug.cgi?id=5958

  $ . $TESTDIR/testlib/common.sh

  $ cat << EOF >> $HGRCPATH
  > [extensions]
  > rebase =
  > evolve =
  > EOF

  $ hg init issue5958
  $ cd issue5958

  $ echo hi > r0
  $ hg ci -qAm 'add r0'
  $ echo hi > foo.txt
  $ hg ci -qAm 'add foo.txt'
  $ hg metaedit -r . -d '0 2'
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved

(Make changes in unrelated files so that we don't have any merge conflicts
during the rebase, but the two touched revisions aren't identical)

date: updated on both side to the same value

  $ echo hi > bar.txt
  $ hg add -q bar.txt
  $ hg amend -q
  $ hg metaedit -r 1 -d '0 1' --hidden
  2 new content-divergent changesets
  $ hg log -r tip
  changeset:   4:c17bf400a278
  tag:         tip
  parent:      0:a24ed8ad918c
  user:        test
  date:        Wed Dec 31 23:59:59 1969 -0000
  instability: content-divergent
  summary:     add foo.txt
  
  $ echo hi > baz.txt
  $ hg add -q baz.txt
  $ hg amend -q
  $ hg rebase -qr tip -d 4
  $ hg log -G
  @  changeset:   6:08bc7ba82799
  |  tag:         tip
  |  parent:      4:c17bf400a278
  |  user:        test
  |  date:        Wed Dec 31 23:59:58 1969 -0000
  |  instability: content-divergent
  |  summary:     add foo.txt
  |
  *  changeset:   4:c17bf400a278
  |  parent:      0:a24ed8ad918c
  |  user:        test
  |  date:        Wed Dec 31 23:59:59 1969 -0000
  |  instability: content-divergent
  |  summary:     add foo.txt
  |
  o  changeset:   0:a24ed8ad918c
     user:        test
     date:        Thu Jan 01 00:00:00 1970 +0000
     summary:     add r0
  
  $ hg obslog -a -r .
  @  08bc7ba82799 (6) add foo.txt
  |
  | *  c17bf400a278 (4) add foo.txt
  | |
  x |  1d1fc409af98 (5) add foo.txt
  | |    rewritten(parent, content) as 08bc7ba82799 using rebase by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  x |  a25dd7af6cf6 (3) add foo.txt
  | |    rewritten(content) as 1d1fc409af98 using amend by test (Thu Jan 01 00:00:00 1970 +0000)
  | |
  x |  0065551bd38f (2) add foo.txt
  |/     rewritten(content) as a25dd7af6cf6 using amend by test (Thu Jan 01 00:00:00 1970 +0000)
  |
  x  cc71ffbc7c00 (1) add foo.txt
       rewritten(date) as 0065551bd38f using metaedit by test (Thu Jan 01 00:00:00 1970 +0000)
       rewritten(date) as c17bf400a278 using metaedit by test (Thu Jan 01 00:00:00 1970 +0000)
  
  $ hg evolve --list --rev .
  08bc7ba82799: add foo.txt
    content-divergent: c17bf400a278 (draft) (precursor cc71ffbc7c00)
  
  $ hg log --hidden -r cc71ffbc7c00 -T '{rev} {node|short} {date|isodate}: {join(obsfate, "; ")}\n'
  1 cc71ffbc7c00 1970-01-01 00:00 +0000: date-changed using metaedit as 4:c17bf400a278; date-changed using metaedit as 2:0065551bd38f
  $ hg log -r 'desc("add foo.txt")' -T '{rev} {node|short} {date|isodate}: {join(obsfate, "; ")}\n'
  4 c17bf400a278 1969-12-31 23:59 -0000: 
  6 08bc7ba82799 1969-12-31 23:59 -0000: 
  $ hg evolve --content-divergent
  merge:[6] add foo.txt
  with: [4] add foo.txt
  base: [1] add foo.txt
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  1 new orphan changesets
  working directory is now at 459c64f7eaad
  $ hg log -r 'desc("add foo.txt")' -T '{rev} {node|short} {date|isodate}: {join(obsfate, "; ")}\n'
  4 c17bf400a278 1969-12-31 23:59 -0000: rewritten using evolve as 7:459c64f7eaad
  7 459c64f7eaad 1969-12-31 23:59 -0000: 

date: updated one one side to an older value

  $ hg evolve -r .
  move:[7] add foo.txt
  atop:[0] add r0
  working directory is now at 545776b4e79f
  $ hg update --hidden --rev 'predecessors(.)'
  1 files updated, 0 files merged, 0 files removed, 0 files unresolved
  updated to hidden changeset 459c64f7eaad
  (hidden revision '459c64f7eaad' was rewritten as: 545776b4e79f)
  working directory parent is obsolete! (459c64f7eaad)
  (use 'hg evolve' to update to its successor: 545776b4e79f)
  $ hg amend --date "0 3"
  1 new orphan changesets
  2 new content-divergent changesets
  $ hg rebase -r . -d 0
  rebasing 9:c117f15338e6 "add foo.txt" (tip)
  $ hg log -G
  @  changeset:   10:7a09c7a39546
  |  tag:         tip
  |  parent:      0:a24ed8ad918c
  |  user:        test
  |  date:        Wed Dec 31 23:59:57 1969 -0000
  |  instability: content-divergent
  |  summary:     add foo.txt
  |
  | *  changeset:   8:545776b4e79f
  |/   parent:      0:a24ed8ad918c
  |    user:        test
  |    date:        Wed Dec 31 23:59:58 1969 -0000
  |    instability: content-divergent
  |    summary:     add foo.txt
  |
  o  changeset:   0:a24ed8ad918c
     user:        test
     date:        Thu Jan 01 00:00:00 1970 +0000
     summary:     add r0
  
  $ hg evolve --list -r .
  7a09c7a39546: add foo.txt
    content-divergent: 545776b4e79f (draft) (precursor 459c64f7eaad)
  
  $ hg log -r 459c64f7eaad+7a09c7a39546+545776b4e79f --hidden -T '{rev} {node|short} {date|isodate}: {join(obsfate, "; ")}\n'
  7 459c64f7eaad 1969-12-31 23:59 -0000: date-changed using amend as 9:c117f15338e6; rebased using evolve as 8:545776b4e79f
  10 7a09c7a39546 1969-12-31 23:59 -0000: 
  8 545776b4e79f 1969-12-31 23:59 -0000: 
  $ hg evolve --content-divergent
  merge:[8] add foo.txt
  with: [10] add foo.txt
  base: [7] add foo.txt
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  working directory is now at 39c4200c0d94
  $ hg log -r . --hidden -T '{rev} {node|short} {date|isodate}: {join(obsfate, "; ")}\n'
  11 39c4200c0d94 1969-12-31 23:59 -0000: 

date: updated one side to an newer value

  $ hg update --hidden --rev 'predecessors(.)'
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  updated to hidden changeset 7a09c7a39546
  (hidden revision '7a09c7a39546' was rewritten as: 39c4200c0d94)
  working directory parent is obsolete! (7a09c7a39546)
  (use 'hg evolve' to update to its successor: 39c4200c0d94)
  $ hg amend --date "120 0"
  2 new content-divergent changesets
  $ hg log -G
  @  changeset:   12:da3be3d72fe2
  |  tag:         tip
  |  parent:      0:a24ed8ad918c
  |  user:        test
  |  date:        Thu Jan 01 00:02:00 1970 +0000
  |  instability: content-divergent
  |  summary:     add foo.txt
  |
  | *  changeset:   11:39c4200c0d94
  |/   parent:      0:a24ed8ad918c
  |    user:        test
  |    date:        Wed Dec 31 23:59:57 1969 -0000
  |    instability: content-divergent
  |    summary:     add foo.txt
  |
  o  changeset:   0:a24ed8ad918c
     user:        test
     date:        Thu Jan 01 00:00:00 1970 +0000
     summary:     add r0
  
  $ hg evolve --list -r .
  da3be3d72fe2: add foo.txt
    content-divergent: 39c4200c0d94 (draft) (precursor 7a09c7a39546)
  
  $ hg up 39c4200c0d94
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  $ hg log -r 7a09c7a39546+39c4200c0d94+da3be3d72fe2 --hidden -T '{rev} {node|short} {date|isodate}: {join(obsfate, "; ")}\n'
  10 7a09c7a39546 1969-12-31 23:59 -0000: date-changed using amend as 12:da3be3d72fe2; rewritten using evolve as 11:39c4200c0d94
  11 39c4200c0d94 1969-12-31 23:59 -0000: 
  12 da3be3d72fe2 1970-01-01 00:02 +0000: 
  $ hg evolve --content-divergent
  merge:[11] add foo.txt
  with: [12] add foo.txt
  base: [10] add foo.txt
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  working directory is now at 06cde6010a51
  $ hg log -r . --hidden -T '{rev} {node|short} {date|isodate}: {join(obsfate, "; ")}\n'
  13 06cde6010a51 1970-01-01 00:02 +0000: 

date: updated each side to a different value, newer should win

  $ hg amend --date "235 0"
  $ hg update --hidden --rev 'predecessors(.)'
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  updated to hidden changeset 06cde6010a51
  (hidden revision '06cde6010a51' was rewritten as: a7412ff9bfb3)
  working directory parent is obsolete! (06cde6010a51)
  (use 'hg evolve' to update to its successor: a7412ff9bfb3)
  $ hg amend --date "784 0"
  2 new content-divergent changesets
  $ hg log -G
  @  changeset:   15:e3077936ec52
  |  tag:         tip
  |  parent:      0:a24ed8ad918c
  |  user:        test
  |  date:        Thu Jan 01 00:13:04 1970 +0000
  |  instability: content-divergent
  |  summary:     add foo.txt
  |
  | *  changeset:   14:a7412ff9bfb3
  |/   parent:      0:a24ed8ad918c
  |    user:        test
  |    date:        Thu Jan 01 00:03:55 1970 +0000
  |    instability: content-divergent
  |    summary:     add foo.txt
  |
  o  changeset:   0:a24ed8ad918c
     user:        test
     date:        Thu Jan 01 00:00:00 1970 +0000
     summary:     add r0
  
  $ hg evolve --list -r .
  e3077936ec52: add foo.txt
    content-divergent: a7412ff9bfb3 (draft) (precursor 06cde6010a51)
  
  $ hg log -r 39c4200c0d94+a7412ff9bfb3+e3077936ec52 --hidden -T '{rev} {node|short} {date|isodate}: {join(obsfate, "; ")}\n'
  11 39c4200c0d94 1969-12-31 23:59 -0000: date-changed using evolve as 13:06cde6010a51
  14 a7412ff9bfb3 1970-01-01 00:03 +0000: 
  15 e3077936ec52 1970-01-01 00:13 +0000: 
  $ hg evolve --content-divergent
  merge:[14] add foo.txt
  with: [15] add foo.txt
  base: [13] add foo.txt
  0 files updated, 0 files merged, 0 files removed, 0 files unresolved
  working directory is now at 1a39f3901288
  $ hg log -r . --hidden -T '{rev} {node|short} {date|isodate}: {join(obsfate, "; ")}\n'
  16 1a39f3901288 1970-01-01 00:13 +0000: 
