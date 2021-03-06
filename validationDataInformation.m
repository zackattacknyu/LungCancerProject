dirName = 'data/stage1/stage1';

dcmFolders = dir(dirName);
numFolders = size(dcmFolders,1);

allPatIDs = cell(1,numFolders);
index=0;
for i = 1:numFolders
    foldname = dcmFolders(i,1).name;
    if(length(foldname) < 4)
       continue; %do not include it 
    end
    
    index = index+1;
    allPatIDs{index} = foldname;
    
end
allPatIDs = allPatIDs(1,1:index);
%%
patIDdict = containers.Map(allPatIDs,ones(1,index));

%%
load('stage1_labelsMAT.mat');
load('sampleImageMetadata.mat');

names = textdata(2:end,1);
%%

namesDictionary = containers.Map(names,labelData);
%%

patIDsample = cell(1,20);
for ii = 1:20
   patIDsample{ii} = dcmInfoArray{ii}{1}.PatientID; 
end

%%

goodPatIDs = find(isKey(namesDictionary,patIDsample));
sampleDataLabels2 = values(namesDictionary,patIDsample(goodPatIDs));

sampleDataWithLabels = cell(length(goodPatIDs),2);
sampleDataWithLabels(:,1) = patIDsample(goodPatIDs);
sampleDataWithLabels(:,2) = sampleDataLabels2;

%%

save('sampleImageLabels.mat','sampleDataWithLabels');

%%

XmatrixFromSample = zeros(19,256*256*100);
YcolumnFromSample = zeros(19,1);
for jj = 1:size(sampleDataWithLabels,1)
    jj
   currentID = sampleDataWithLabels{jj,1};
   curName = strcat('resizedSegDCM_',currentID,'.mat');
   load(curName);
   XmatrixFromSample(jj,:)=(resizedDCM(:))';
   
   YcolumnFromSample(jj,1)=sampleDataWithLabels{jj,2};
end

mnrfit(X,Y)
