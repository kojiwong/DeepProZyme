# import torch packages
import torch
import torch.nn as nn


class DeepECv2(nn.Module):
    def __init__(self, out_features):
        super(DeepECv2, self).__init__()
        self.explainECs = out_features
        # self.embedding = nn.Embedding(1000, 21) # 20 AA + X + blank
        self.cnn0 = CNN0()
        self.fc = nn.Linear(in_features=128*3, out_features=len(out_features))
        self.bn1 = nn.BatchNorm1d(num_features=len(out_features))
        self.out_act = nn.Sigmoid()
        self.init_weights()


    def init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.xavier_uniform_(m.weight)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)

        
    def forward(self, x):
        # x = self.embedding(x)
        x = self.cnn0(x)
        x = x.view(-1, 128*3)
        x = self.out_act(self.bn1(self.fc(x)))
        return x


class CNN0(nn.Module):
    '''
    Use second level convolution.
    channel size: 4 -> 16 
                  8 -> 12
                  16 -> 4
    '''
    def __init__(self):
        super(CNN0, self).__init__()
        self.relu = nn.ReLU()
        self.dropout = nn.Dropout(p=0.1)
           
        self.conv1 = nn.Conv2d(in_channels=1, out_channels=128, kernel_size=(4,21))
        self.conv2 = nn.Conv2d(in_channels=1, out_channels=128, kernel_size=(8,21))
        self.conv3 = nn.Conv2d(in_channels=1, out_channels=128, kernel_size=(16,21))

        self.batchnorm1 = nn.BatchNorm2d(num_features=128)
        self.batchnorm2 = nn.BatchNorm2d(num_features=128)
        self.batchnorm3 = nn.BatchNorm2d(num_features=128)

        self.conv1_1 = nn.Conv2d(in_channels=128, out_channels=128, kernel_size=(16,1))
        self.conv2_1 = nn.Conv2d(in_channels=128, out_channels=128, kernel_size=(12,1))
        self.conv3_1 = nn.Conv2d(in_channels=128, out_channels=128, kernel_size=(4,1))

        self.batchnorm1_1 = nn.BatchNorm2d(num_features=128)
        self.batchnorm2_1 = nn.BatchNorm2d(num_features=128)
        self.batchnorm3_1 = nn.BatchNorm2d(num_features=128)

        self.conv = nn.Conv2d(in_channels=128*3, out_channels=128*3, kernel_size=(1,1))
        self.batchnorm = nn.BatchNorm2d(num_features=128*3)
        self.pool = nn.MaxPool2d(kernel_size=(982,1), stride=1)

        
    def forward(self, x):
        x1 = self.dropout(self.relu(self.batchnorm1(self.conv1(x))))
        x2 = self.dropout(self.relu(self.batchnorm2(self.conv2(x))))
        x3 = self.dropout(self.relu(self.batchnorm3(self.conv3(x))))
        x1 = self.dropout(self.relu(self.batchnorm1_1(self.conv1_1(x1))))
        x2 = self.dropout(self.relu(self.batchnorm2_1(self.conv2_1(x2))))
        x3 = self.dropout(self.relu(self.batchnorm3_1(self.conv3_1(x3))))

        x = torch.cat((x1, x2, x3), dim=1)
        x = self.relu(self.batchnorm(self.conv(x)))
        x = self.pool(x)
        return x


class DeepECv2_2(nn.Module):
    def __init__(self, out_features):
        super(DeepECv2_2, self).__init__()
        self.explainECs = out_features
        self.cnn0 = CNN1()

        self.fc1 = nn.Linear(in_features=128*2, out_features=512)
        self.bn1 = nn.BatchNorm1d(num_features=512)
        self.fc2 = nn.Linear(in_features=512, out_features=len(out_features))
        self.bn2 = nn.BatchNorm1d(num_features=len(out_features))
        self.out_act = nn.Sigmoid()
        self.relu = nn.ReLU()
        
        self.init_weights()


    def init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.xavier_uniform_(m.weight)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)

        
    def forward(self, x):
        x = self.cnn0(x)
        x = x.view(-1, 128*2)
        x = self.relu(self.bn1(self.fc1(x)))
        x = self.out_act(self.bn2(self.fc2(x)))
        return x


class CNN1(nn.Module):
    def __init__(self):
        super(CNN1, self).__init__()
        conv_module = [
            nn.Conv2d(in_channels=1, out_channels=128, kernel_size=(4,21)),
            nn.BatchNorm2d(num_features=128),
            nn.ReLU(),
            nn.Dropout(p=0.1)
        ]

        conv_module += [
            nn.Conv2d(in_channels=128, out_channels=128*2, kernel_size=(4,1)),
            nn.BatchNorm2d(num_features=128*2),
            nn.ReLU(),
            nn.Dropout(p=0.1)
        ]

        conv_module += [
            nn.Conv2d(in_channels=128*2, out_channels=128*2, kernel_size=(4,1)),
            nn.BatchNorm2d(num_features=128*2),
            nn.ReLU(),
            nn.Dropout(p=0.1)
        ] * 4

        self.conv_layers = nn.Sequential(*conv_module)
        
        self.conv = nn.Conv2d(in_channels=128*2, out_channels=128*2, kernel_size=(1,1))
        self.batchnorm = nn.BatchNorm2d(num_features=128*2)
        self.pool = nn.MaxPool2d(kernel_size=(982,1), stride=1)
        self.relu = nn.ReLU()

        
    def forward(self, x):
        x = self.conv_layers(x)
        x = self.relu(self.batchnorm(self.conv(x)))
        x = self.pool(x)
        return x


class DeepECv2_3(nn.Module):
    def __init__(self, out_features):
        super(DeepECv2_3, self).__init__()
        self.explainECs = out_features
        # self.embedding = nn.Embedding(1000, 21) # 20 AA + X + blank
        self.cnn0 = CNN0()
        self.fc1 = nn.Linear(in_features=128*3, out_features=512)
        self.bn1 = nn.BatchNorm1d(num_features=512)
        self.fc2 = nn.Linear(in_features=512, out_features=len(out_features))
        self.bn2 = nn.BatchNorm1d(num_features=len(out_features))
        self.relu = nn.ReLU()
        self.out_act = nn.Sigmoid()
        self.init_weights()


    def init_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.xavier_uniform_(m.weight)
            elif isinstance(m, nn.Linear):
                nn.init.xavier_uniform_(m.weight)

        
    def forward(self, x):
        x = self.cnn0(x)
        x = x.view(-1, 128*3)
        x = self.relu(self.bn1(self.fc1(x)))
        x = self.out_act(self.bn2(self.fc2(x)))
        return x