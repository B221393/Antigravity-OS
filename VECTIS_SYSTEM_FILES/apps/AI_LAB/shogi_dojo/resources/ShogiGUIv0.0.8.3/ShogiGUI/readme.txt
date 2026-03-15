ShogiGUI

USIプロトコルに対応した将棋GUIソフトです。

■必要環境
●ver 0.0.8.0以降
 .NET framework 4.8.1

●ver 0.0.8.0以前
Windows Vista 以降
.NET Framework 4.5

.NETが4.5以上無駄に必要ですので、Windows XPは未対応です。

同梱のgpsfishは64bitOSでのみ動作します。
32bitOSの方はオリジナルのgpsfishをご使用ください。

■インストール、アンインストール方法
・zip版
解凍したファイルを任意のフォルダに置くだけでインストール完了です。
アンインストールするときは、フォルダごと削除してください。

※"WindowsによってPCが保護されました"と表示される場合、下記サイトなどが参考になるかと思います。
http://support.biglobe.ne.jp/faq/windows8/win8_320.html

・インストーラ版
ダウンロードしたexeファイルを実行するとインストーラーが起動します。
選択しながら次へを押していくとインストールが完了します。

アンインストールはプログラムと機能からアンインストールするか、
スタートメニュー->プログラム->ShogiGUI->uninstallを実行してください。


.NET frameworkのランタイムが必要ですので、インストールされていない場合は各自インストールしてください。


■免責事項
本ソフトウェアを使用して生じたいかなる損害に対しても、開発者は責任を負いません。
自己責任でご使用ください。

■謝辞
ドイツ語の翻訳はAndreas Hausmannさんにして頂きました。
スペイン語の翻訳はGabriel Saavedra from Club Shogi Valdiviaさんにしていただきました。

ありがとうございます。

■更新履歴

2024/2/5 ver 0.0.8.3
 ヘルプ->使い方のURL変更
 定跡のゲーム数、勝率で並べ替え表示　(定跡ヘッダのダブルクリック)
 検討モード alt + テンキー1,2,3でランクに応じた手を指す
 棋譜解析一覧での例外対策

2023/7/18 ver 0.0.8.2
 定跡ツリーのバグ対策
 棋譜解析後の読み筋追加の修正
 画像ファイルにファイル名付与
 ウインドウのリセット対応


2023/4/28 ver 0.0.8.1
 棋譜と定跡のコメント検索に対応

2023/3/11 ver 0.0.8.0
 NET frameworkを4.5 -> 4.8.1へ変更 (VS2022に4.5がなかったため)
 将棋盤の画像コピーにショートカットを割り当てる(Ctrl+Shift+C)
 エンジン別のグラフを表示

2022/9/16 ver 0.0.7.30
 対局中に後手番のヒントで思考が表示されない不具合修正

2022/7/16 ver 0.0.7.29
 vre 0.0.7.28でいれた棋譜コメ削除時に評価値を更新で、棋譜コメの評価値が正しく読めなくなっていたのを修正

2022/7/14 ver 0.0.7.28
 棋譜解析のMultiPVを10まで選択可能にする
 Webからの棋譜取り込みの自動更新に対応
 棋譜コメ削除時に評価値を更新

2022/4/21 ver 0.0.7.27
 入玉宣言->入玉勝ちに変更
 情報windowをメニューからアクティブした時に画面外ならデフォルト位置に戻す
 棋譜解析の一致率を棋譜コメにいれるのをオプションで選べるようにする
 思考エンジン名に▲or△を入れる

2021/11/21 ver 0.0.7.26
 -dオプションで起動時にwindowがアクティブにならない不具合修正

2021/11/18 ver 0.0.7.25
	nps表示を変更、スレッド数表示枠を大きめにする
	解析一覧から一括分岐追加が動作していない不具合修正
	isreadyのタイムアウト時間を１分から５分に変更
	定跡のフォルダから追加でサブフォルダからも追加できるようにする
	連続対局で人でも連続対局できるようにする


2021/5/22 ver 0.0.7.24
    王手されている局面の詰み探索で不要なチェックをはずす
	WEBからの棋譜取り込みで王位戦等のサイト対応
	解析一覧からの分岐追加が段がずれてる問題修正
    

2021/1/6 ver 0.0.7.23
	COM対局後棋譜リストの表示が変になる場合があるのを修正
	棋譜コメ最後の空行は削除する
	MONOでImageListが動かないようなのでその対応

2020/10/31 ver 0.0.7.22
	CSAの読み筋付きコメントのパースエラー時の不具合修正

2020/9/10 ver 0.0.7.21
	初期局面で棋譜解析結果の矢印が出ない不具合修正と色太さ変更
	英語の棋譜解析結果でランクの数値が正しく読めていない不具合修正


2020/7/31 ver 0.0.7.20
	棋譜解析の評価値グラフでランクが無視される不具合修正

2020/7/31 ver 0.0.7.19
	棋譜解析のやねさん対応

2020/7/6 ver 0.0.7.18
	しおりに第5章 図4とか入っていた場合その値でソートするオプション追加

2020/4/8 ver 0.0.7.17
	英語表記で段を数字アルファベット漢数字がから選べるようにする
	新規、対局、局面編集時も自動保存の対象にする
	ダイアログをESCで閉じる

2020/2/5 ver 0.0.7.16
    将棋ウォーズ棋譜読み込み新しい形式に対応

2020/1/9 ver 0.0.7.15
	局面編集後駒箱表示が残る不具合修正
	ライブラリアップデート
	  DockPanelSuite 3.0.6 <= 3.0.4
	  protobuf-net 2.4.4 <= 2.0.0.668
	一定間隔で自動保存する機能を追加
	評価値グラフ対局時のグラフ（白と黒）太くする
	細かいバグ修正


2019/11/13 ver 0.0.7.14
	棋譜コピーしたユニバーサル型式の貼り付け対応
	こまごまバグ修正

2019/10/23 ver 0.0.7.13
	分岐のタブ幅を広くする
	棋譜の移動が遅い？の暫定対策

2019/10/17 ver 0.0.7.12
   棋譜解析時非合法局面の棋譜を解析しない
   コメントに記録した解析結果の矢印表示
   評価値グラフの悪手表示を▲▼にする


2019/08/31 ver 0.0.7.11
   棋譜解析の時間、ノード、深さ（movetime,nodes,depth）指定の時にgoコマンドの区切りスペースが入ってない不具合修正

2019/06/26 ver 0.0.7.10
   棋譜解析時にstringとpvが両方出力された場合はpvを優先する
   全ての駒を駒箱に移動するメニューを追加

2019/05/29 ver 0.0.7.9
   樹形図の上限撤廃
   WEBから棋譜取り込みの文字コード判別を変更
   ダイアログにutf-8用のフィルタを追加

2019/03/04 ver 0.0.7.8
   BODの指し手を修正

2019/02/25 ver 0.0.7.7
   BODの指し手を修正

2019/02/11 ver 0.0.7.6
   スペイン語文言を修正

2019/02/06 ver 0.0.7.5
	BODに手数と最終手を出力するように変更
	将棋ウォーズの棋譜一覧URLを修正

2018/12/17 ver 0.0.7.4
	WEBからの棋譜取り込みTLS1.1,1.2対応
	sfenの局面コピーにsfenを付ける
	将棋ウォーズ棋譜一覧表示

2018/12/05 ver 0.0.7.3
	スペイン語対応

2018/10/19 ver 0.0.7.2
	CSAファイル読み込み時に手合い割が重複するバグ修正
	棋譜ペースト時の判定を修正
	フォント変更に対応
	DockPanelSuiteのバージョンを3.04にする

2018/10/11 ver 0.0.7.1
	高DPI時のレイアウト崩れ修正
	駒箱
	評価値グラフのドット色が常に緑になる不具合修正

2018/10/3 ver 0.0.7.0
	高DPI対応（※簡易対応で一部レイアウト崩れあり）
	棋譜解析にエンジン名を入れる

2018/9/27 ver 0.0.6.15
	内部で使ってるハッシュ値を修正
	棋譜欄のコメント表示対応
	コマの移動元、移動先の透明度を設定に対応
	URLの貼り付けで棋譜を読み込めるように変更
	文言修正


2018/6/28 ver 0.0.6.14
    KIF形式のしおりに対応
	他バグ修正

2018/5/31 ver 0.0.6.13
    伝統表記修正
	解析一覧のタブ幅保存の不具合修正
	MPV時Ctrl+Mでランク１(最善手)を指すように修正

2018/4/11 ver 0.0.6.12
	伝統表記修正
	継盤でコマ選択中は右クリックでコンテキストメニューを表示しないように変更
	定跡の評価値に詰みが入れられない不具合修正
	棋譜解析から評価値等を定跡に追加できるように修正
	他不具合修正

2017/6/21 ver 0.0.6.11
    読み筋に投了、千日手等を表示

2017/3/14 ver 0.0.6.10
	解析一覧からの操作不具合修正

2017/2/2 ver 0.0.6.9
	連続棋譜解析でエラー棋譜はスキップ
	WEBから棋譜取り込みに対応 (ShogiDroidの機能 + 更新時は棋譜をマージする)

2017/1/17 ver 0.0.6.8
	評価値グラフの線形、非線形切り替えオプションを追加

2016/10/14 ver 0.0.6.7
	ホームページを新サイトに変更
	他バグ修正

2016/10/20 ver 0.0.6.6
	駒落ち連続対局の不具合修正
	棋譜解析でマルチPVに対応


2016/10/17 ver 0.0.6.5
    定跡コメント1行表示処理のバグ修正

2016/10/17 ver 0.0.6.4
	分岐も矢印表示する
	グラフに指し手評価表示

	定跡コメントを１行表示する
	定跡作成時に局面数が初期化されない不具合修正


2016/9/7 ver 0.0.6.3
	ヒント表示の優先順修正


2016/8/29 ver 0.0.6.2
	ドイツ語文言追加

2016/8/16 ver 0.0.6.1
	エンジン削除時に例外が発生する不具合修正
	検討モードの評価表示が数値のみなっている不具合修正

2016/8/15 ver 0.0.6.0
	エンジン一覧の並べ替え
	複数エンジンでの検討
	10秒前に音を鳴らす
	他バグ修正
	
2016/7/15 ver 0.0.5.10
	棋譜タブを詰みあり表示にする
	検討モードの候補手をエンジンが返す手すべて表示する
	詰み探索中のbestmoveを無視する

2016/6/25 ver 0.0.5.9
	棋譜解析で悪手率表示を追加
	ヒントの矢印調整

2016/6/20 ver 0.0.5.8
	定跡手を指した時に思考情報が消えない不具合修正
	エンジンの優先度設定
	ヒント、検討時の矢印表示の描画方法変更
	他バグ修正

2016/6/15 ver 0.0.5.7
	連続対局結果を棋譜コメントに保存するオプション追加
	棋譜読み込み後の局面指定オプション追加
	他バグ修正

2016/5/27 ver 0.0.5.6
	node,depth指定の思考と詰み探索が正常に動作しないのを修正(ver 0.0.5.5のエンバグ)
	他バグ修正

2016/5/24 ver 0.0.5.5
	Ponder時の時間設定を修正
	他バグ修正

2016/4/17 ver 0.0.5.4
	棋譜解析情報が複数あった場合、解析一覧の評価値がおかしいのを修正
	棋譜コメントに数値が入力できなくなっていたのを修正
	他バグ修正

2016/4/11 ver 0.0.5.3
	伝統形式の時に読み筋に打が表示されない不具合修正
	解析一覧ウインドウのカレント位置色変え、評価値差分表示
	棋譜解析、検討モードで指し手をすべて送るオプション追加
	他バグ修正

2016/3/14 ver 0.0.5.2
	KI2形式の棋譜コピーで相対位置が出力されなくなっていた不具合修正

2016/3/11 ver 0.0.5.1
	棋譜から読み込んだ評価値グラフが描画しなくなっていた不具合修正
	他バグ修正

2016/2/26 ver 0.0.5.0
	英語対応
	伝統形式とユニバーサル形式の棋譜表記追加
	検討モードで候補手を指す
	他バグ修正


2015/12/23 ver 0.0.4.16
	詰み探索結果を分岐に追加できないバグを修正

2015/12/23 ver 0.0.4.15
	棋譜解析一覧選択時の不具合修正


2015/12/20 ver 0.0.4.14
	棋譜解析悪手率の表示追加
	棋譜解析の読み筋の表示の仕方、棋譜コメントの書式を変更
	他バグ修正
	

2015/10/31 ver 0.0.4.13
	定跡ダイアグラム、ツリーダイアグラムの右クリックで選択がずれるバグ修正
	ツリーダイアグラムの合流表示の強調表示に対応

2015/10/11 ver 0.0.4.12
	詰み探索の時間設定を修正
	他バグ修正

2015/9/19 ver 0.0.4.11
	棋譜コメントの読み筋読み込み修正
	他バグ修正

2015/9/12 ver 0.0.4.10
	棋譜解析のオプションと解析一覧を変更
	定跡の新規作成時に確認ダイアログ追加
	局面編集中に定跡ツリーの選択禁止
	検討モードの時間表示を追加
	他バグ修正


2015/8/30 ver 0.0.4.9
	定跡ツリーの不具合をいくつか修正

2015/8/23 ver 0.0.4.8
	定跡を手動で追加した時にルートにポジション情報が入らないのを修正
	
2015/8/01 ver 0.0.4.7
	指し手の封じ手を中断扱いにする
	定跡の採用率が0%になる不具合修正
	他バグ修正
	
2015/7/12 ver 0.0.4.6
	評価値グラフのスクロール修正
	ツリーダイアグラムの合流表示
	他バグ修正

2015/7/4 ver 0.0.4.5
	連続対局に先後入れ替えOn/Offを追加
	定跡をKIF形式でエクスポートに対応


2015/6/12 ver 0.0.4.4
	棋譜解析時に例外が出るバグを修正

2015/5/31 ver 0.0.4.3
	インストーラーをInno Setupに変更
	使い方のURLを変更


2015/5/17 ver 0.0.4.2
	分岐でコンテキストメニューが開かない不具合修正
	他バグ修正

2015/5/9 ver 0.0.4.1
	対局時の定跡選択条件変更
	手番指定の棋譜からの定跡追加対応
	採用されない定跡のグレー表示
	他バグ修正

2015/5/3 ver 0.0.4.0
	定跡対応　https://sites.google.com/site/shogigui/manual/book
	時間切れタイマーバグ修正
	他バグ修正

	※ShogiGUIは開発中のソフトウェアです。定跡ファイルのフォーマットは予告なく変更する可能性があります。

2015/4/23 ver 0.0.3.17
	Blunderで定跡手を指した時に例外が出る不具合修正

2015/4/8 ver 0.0.3.16
	ヒント、詰み探索時にnewgameが送信されていない不具合修正
	手合割が出力されない不具合修正
	他バグ修正

2015/4/3 ver 0.0.3.15
	パス(null move)の対応
	アシスタント(簡易検討機能）の実装
	検討モードでヒントと詰み探索が動作するように変更
	他バグ修正
	
2015/3/18 ver 0.0.3.14
	0.0.3.9以降でCSAファイルの読み筋がおかしくなっていた不具合修正
	usi->usiokまでのタイムアウトを10秒から30秒に変更

2015/3/12 ver 0.0.3.13
	タイトルに棋譜の情報 or ファイル名を表示する。
	対局時以外の駒音再生不具合修正

2015/2/27 ver 0.0.3.12
	Linuxで動作させた時の不具合を幾つか修正
	Ponder or USI_PonderがFALSEの場合はgo ponderを送らないようにする
	他バグ修正

2015/2/21 ver 0.0.3.11
	0.0.3.9以降で読み筋表示がおかしくなっていた不具合修正
	他バグ修正


2015/2/14 ver 0.0.3.10
	0.0.3.9で局面編集が正常に動作しなくなっていた不具合修正

2015/2/13 ver 0.0.3.9
	棋譜の自動再生
	駒移動アニメーション
	内部構造変更
	他バグ修正

2015/1/22 ver 0.0.3.8
	棋譜解析時の時間指定をmovetimeか従来の指定に戻す。（bonadapter対策）
	局面ペディア対応 ( 編集->局面ペディア)

2015/1/20 ver 0.0.3.7
	棋譜解析時の時間設定、条件を変更
	評価値グラフのカーソル位置表示
	他バグ修正

2014/11/06 ver 0.0.3.6
    CSA形式棋譜の評価値が逆なのを修正

2014/11/03 ver 0.0.3.5
    CSA形式の棋譜の読み筋(fgや電王トーナメントの棋譜）を表示
	千日手の履歴がクリアされないバグ修正
	ツリーダイアグラムの文字強調表示がおかしくなっていたのを修正

2014/8/19 ver 0.0.3.4
	棋譜解析一覧のカーソル移動不具合修正
	将棋盤のサイズが変になる不具合修正
	他バグ修正

2014/7/9 ver 0.0.3.3
	コマ落ち棋譜読み込み不具合修正
	棋譜連続解析
	

2014/6/25 ver 0.0.3.2
	詰みボタンの挙動がおかしくなっていたのを修正
	対局開始ダイアログで先後入れ替え、振り駒
	思考の矢印表示
	コメントに入れた思考情報を"i"表示するように変更
	他バグ修正

2014/6/19 ver 0.0.3.1
	拡大倍率変更でレイアウトが崩れる問題修正
	他バグ修正

2014/6/13 ver 0.0.3.0
	駒操作のドラッグ＆ドロップ対応（オプションで有効、無効設定）
	ダブルクリックで指し手移動のところをシングルクリック or 選択に変更
	検討モード、棋譜解析に深さ指定、ノード数指定を追加
	入力取り消し
	
	いろいろバグ修正

2014/6/5 ver 0.0.2.0
	将棋盤の罫線の色変更
	検討ウインドウ追加
	不具合修正

2014/5/30 ver 0.0.1.2
	局面編集
	対局中の待った、すぐに指すボタン追加
	
	いろいろ不具合修正
	
2014/5/23 ver 0.0.1.1
	連続対局時の先後入れ替え
	
	
2014/5/23 ver 0.0.1.0
	α版
	
	連続対局
	棋譜自動保存
	検討モードで時間指定
	銀桂香の成り表記を変更
	コントロールパネルに盤面回転ボタンを追加
	評価値グラフをスクロール可能にする
	ホイール操作で指し手進む、戻る
	
	成り判定不具合修正
	棋譜コメントにスクロールバーを追加
	継ぎ盤のサイズ保存と音声再生を修正
	他、不具合修正
	
	
2014/5/14 ver 0.0.0.9
	GPSFishの定跡データを使った定跡表示に対応
	詰み探索の時間設定不具合を修正
	いくつかの不具合修正

2014/5/8 ver 0.0.0.8
	駒を掴む操作の変更（ハム将棋と同じ、ダウンで掴む、クリックで置く）
	分岐追加時の動作変更
	ツリーダイアログで分岐マージ機能追加
	Undo/Redo機能追加
	千日手を自動判定
	棋譜のコピー、ペーストのショートカット対応
	いくつかの不具合修正
	
2014/4/29 ver 0.0.0.7
	後手時間表示、先手のエンジンへの時間通知を修正

2014/4/22 ver 0.0.0.6
	分岐追加で例外が発生するバグを修正

2014/4/22 ver 0.0.0.5
	エンジンの読み筋を分岐に追加、継ぎ盤で表示
	駒、盤など外部ファイルの読み込み
	CSA棋譜の貼り付け対応
	いくつかの不具合修正
	
2014/4/10 ver 0.0.0.4
	ツリーダイアグラム表示対応
	いくつかの不具合修正

2014/4/6 ver 0.0.0.3
	CSA棋譜読み込み対応
	いくつかの不具合修正

2014/4/2 ver 0.0.0.2
	盤面とグラフの画像コピー、WEB局面図のURL作成
	Ponderコマンド対応
	棋譜解析
	いくつかの不具合修正

2014/3/28 ver 0.0.0.1
	試作版公開


■ライセンス

同梱してある将棋エンジンGPSFishのライセンスはengine\gpsfishフォルダ内にあるライセンスをお読みください。

GPSFishオリジナルのバイナリとソースコードの入手先
http://gps.tanaka.ecc.u-tokyo.ac.jp/gpsshogi/index.php?%A5%C0%A5%A6%A5%F3%A5%ED%A1%BC%A5%C9

GPSFish同梱版のバイナリとソースコード
https://sites.google.com/site/shogixyz/home/gpsfish



本ソフトウェアは下記のサイトの画像、アイコンを利用しています。

・ikons(http://ikons.piotrkwiatkowski.co.uk/)


本ソフトウェアは下記のソフトウェアを利用しています。

・ReadJEnc https://github.com/hnx8/ReadJEnc

https://github.com/hnx8/ReadJEnc/blob/master/LICENSE


・DockPanel Suite

The MIT License

Copyright (c) 2007 Weifen Luo (email: weifenluo@yahoo.com)

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

・Protocol Buffers

The core Protocol Buffers technology is provided courtesy of Google.
At the time of writing, this is released under the BSD license.
Full details can be found here:

http://code.google.com/p/protobuf/


This .NET implementation is Copyright 2008 Marc Gravell

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


本ソフトウェアでGPSFishの定跡ファイルにアクセスしている部分は、OSLライブラリを直接使用してはいませんが、以下のライセンスとなります。

License of OSL (Open Shogi Library) †
Copyright 2003 Team GPS, the University of Tokyo. All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE TEAM GPS ``AS IS'' AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE TEAM GPS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

The views and conclusions contained in the software and documentation are those of the authors and should not be interpreted as representing official policies, either expressed or implied, of the Team GPS.

Copyright 2003 Team GPS, the University of Tokyo. All rights reserved.

ソースコード形式であれバイナリ形式であれ、変更の有無に 関わらず、以下の条件を満たす限りにおいて、再配布してかまいません:

ソースコード形式で再配布する場合、上記著作権表示、 本条件書および下記責任限定規定を必ず含めてください。

バイナリ形式で再配布する場合、上記著作権表示、 本条件書および下記責任限定規定を、配布物とともに提供される文書 および/または 他の資料に必ず含めてください。

本ソフトウェアは Team GPS によって、”現状のまま” 提供されるものとします。 本ソフトウェアについては、明示黙示を問わず、 商用品として通常そなえるべき品質をそなえているとの保証も、 特定の目的に適合するとの保証を含め、何の保証もなされません。 事由のいかんを問わず、 損害発生の原因いかんを問わず、且つ、 責任の根拠が契約であるか厳格責任であるか (過失その他) 不法行為であるかを問わず、 Team GPS も寄与者も、 仮にそのような損害が発生する可能性を知らされていたとしても、 本文書の使用から発生した直接損害、間接損害、偶発的な損害、特別損害、 懲罰的損害または結果損害のいずれに対しても (代替品または サービスの提供; 使用機会、データまたは利益の損失の補償; または、業務の中断に対する補償を含め) 責任をいっさい負いません。

このソフトウェアと文書に含まれる意見や結論はそれらの著作者による ものであって、Team GPS の 公式な方針を、明示黙示を問わず、あらわしているものと とってはならない。

