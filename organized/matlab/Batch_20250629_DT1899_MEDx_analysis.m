%2025/06/29
%DT1899 MEDx data analysis only (without photometry)
%Based on Batch_20250625_test_Goonly.m algorithm
%TIME AXIS CORRECTED VERSION - E event (Go cue) as time 0
%
%Schedule: FI5 (Fixed Interval 5 seconds)

%%
name='DT1899';
Day = '_20250629';

variable = strcat(name, Day, '_training.mat') ;

Ws = 20;
We = 50;
Hz = 10;

%%
% TIME AXIS DEFINITION (E = Go cue at time 0)
% E = Go cue (event1, CSp)         0 sec (reference point)
% B = Hit cue                      1 sec after Go cue
% H = miss cue                     1 sec after Go cue
% C = Licks,                       recorded throughout
% N = 1st Lick,                    recorded throughout
% Judgment window: 0-1 sec after Go cue

% Original index definitions:
% B = Hit cue                      10,    7  (index_B)
% C = Licks,                       10+1, 10  (index_B+1)
% E = event1, CSp reward,          10+3, 12  (index_B+3) <- Go cue
% F = event4, CSm omission,        10+4, 13
% H = miss cue                     10+6, 15  (index_B+6)
% N = 1st Lick,                    10+8, 17  (index_B+8)
% O = False alarm cue,             10+9, 18
% Q = correct response cue,        10+10, 19
% R = Licks, event1, CSp reward,   10+11,20  (index_B+11)
% V = Licks, event4, CSm omission, 10+12,21

CS_time = 1; % Go cue duration (correct as is)

%%
%Batch file
addpath('D:\DN001_Programs')%functionがあるルートディレクトリの絶対パス
fL_event = @MED_rasterize_wo_1stLick_2con_CSp_operant;

%%
% テキストファイルの読み込み
txt_file = 'D:\DN001_TF\2025_G00(DT1878,1899,1909)\Data_raw\20250629_DT1899_MEDx.txt';

% データの読み込み
ipt_data = readmatrix(txt_file);%.txtの-7行になっている/7行目にAが来る
endlength = length(ipt_data);

TF = ismissing(ipt_data);
ipt_data(:,3) = [];
ipt_data(:,1) = [];%必要な2列目のみを残した
T_s = cumsum(TF);%Dが6になっている/0,1の行列を列ごとに累積加算した行列を作成し、文字をその数字で探す
T_s(:,3) = [];
T_s(:,1) = [];%必要な2列目のみを残した

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%データのインポート
box = cat(2,ipt_data, T_s);
index_B = box(18,2);

%Reward
for i = endlength:-1:1
    if box(i,1) >= 0 && box(i,2) == index_B
    else
        box(i,:) = [];
    end
        reward_cue = box;
        reward_cue(:,2)=[];
end

box = cat(2,ipt_data, T_s);
%Licks
for i = endlength:-1:1
    if box(i,1) >= 0 && box(i,2) == index_B+1
    else
        box(i,:) = [];
    end
    Licks = box;
    Licks(:,2)=[];
end 

box = cat(2,ipt_data, T_s);
%event1 CSp reward (Go cue - CRITICAL FOR TIME REFERENCE)
for i = endlength:-1:1
    if box(i,1) >= 0 && box(i,2) == index_B + 3
    else
        box(i,:) = [];
    end
        event1 = box;
        event1(:,2)=[];
end 
Go_cue = event1;  % E event is the Go cue (time 0 reference)

box = cat(2,ipt_data, T_s);
%miss cue
for i = endlength:-1:1
    if box(i,1) >= 0 && box(i,2) == index_B + 6
    else
        box(i,:) = [];
    end
        miss_cue = box;
        miss_cue(:,2)=[];
end

box = cat(2,ipt_data, T_s);
%1st lick
for i = endlength:-1:1
    if box(i,1) >= 0 && box(i,2) == index_B + 8
    else
        box(i,:) = [];
    end
        Licks_1st = box;
        Licks_1st(:,2)=[];
end

box = cat(2,ipt_data, T_s);
%Licks_event1
for i = endlength:-1:1
    if box(i,1) >= 0 && box(i,2) == index_B + 11
    else
        box(i,:) = [];
    end
        Licks_event1 = box;
        Licks_event1(:,2)=[];
end

box = cat(2,ipt_data, T_s);
%Hit Cue
for i = endlength:-1:1
    if box(i,1) >= 0 && box(i,2) == index_B+13
    else
        box(i,:) = [];
    end
    Hit_cue = box;
    Hit_cue(:,2)=[];
end 

% CRITICAL TIME AXIS CORRECTION
% E event (Go cue) is time 0 for ALL trials
% Use Go_cue directly without any time subtraction

%%
%function start
% Pass Go cue times (time 0) for all trials
result_Licks = fL_event('DT1899_Licks',Licks,Go_cue,Go_cue,Ws/Hz,We/Hz);

%%
close all
save(variable)