import torch
from torch import nn


class convNet(nn.Module):
    def __init__(self, channels):
        super(convNet, self).__init__()

        self.parse = nn.Sequential(
            nn.Conv1d(
                in_channels=channels,
                out_channels=channels,
                stride=1,
                kernel_size=3,
                padding=1
            ),
            nn.Conv1d(
                in_channels=channels,
                out_channels=channels,
                stride=1,
                kernel_size=3,
                padding=1
            ),
            nn.Conv1d(
                in_channels=channels,
                out_channels=channels,
                stride=1,
                kernel_size=3,
                padding=1
            ),
            nn.PReLU()
        )

    def forward(self, x):
        return self.parse(x)


class hNet_RL_v1(nn.Module):
    def __init__(self, board_size, res_net_layer_number=16):
        super().__init__()

        self.conv_size = [1, 16, 32]

        self.get_mask = nn.Sequential(
            nn.Conv1d(1, 1, kernel_size=1, stride=1),
            nn.Tanh(),
            nn.Conv1d(1, 1, kernel_size=1, stride=1),
            nn.Tanh()
        )

        self.catch = nn.Sequential(
            nn.Conv1d(
                in_channels=self.conv_size[0],
                out_channels=self.conv_size[1],
                stride=1, kernel_size=3, padding=1
            ),
            nn.Conv1d(
                in_channels=self.conv_size[1],
                out_channels=self.conv_size[1],
                stride=1, kernel_size=3, padding=1
            ),
            nn.Conv1d(
                in_channels=self.conv_size[1],
                out_channels=self.conv_size[1],
                stride=1, kernel_size=3, padding=1
            ),
            nn.Softplus(),
            nn.Conv1d(
                in_channels=self.conv_size[1],
                out_channels=self.conv_size[2],
                stride=1, kernel_size=3, padding=1
            ),
            nn.Conv1d(
                in_channels=self.conv_size[2],
                out_channels=self.conv_size[2],
                stride=1, kernel_size=3, padding=1
            ),
            nn.Conv1d(
                in_channels=self.conv_size[2],
                out_channels=self.conv_size[2],
                stride=1, kernel_size=3, padding=1
            ),
            nn.Softplus(),
        )

        self.resNet = nn.ModuleList(
            [convNet(self.conv_size[2]) for _ in range(res_net_layer_number)]
        )

        self.push = nn.Sequential(
            nn.Conv1d(
                in_channels=self.conv_size[2],
                out_channels=self.conv_size[1],
                stride=1, kernel_size=3, padding=1
            ),
            nn.Conv1d(
                in_channels=self.conv_size[1],
                out_channels=self.conv_size[1],
                stride=1, kernel_size=3, padding=1
            ),
            nn.Conv1d(
                in_channels=self.conv_size[1],
                out_channels=self.conv_size[1],
                stride=1, kernel_size=3, padding=1
            ),
            nn.PReLU(),
            nn.Conv1d(
                in_channels=self.conv_size[1],
                out_channels=self.conv_size[0],
                stride=1, kernel_size=3, padding=1
            ),
            nn.Conv1d(
                in_channels=self.conv_size[0],
                out_channels=self.conv_size[0],
                stride=1, kernel_size=3, padding=1
            ),
            nn.Conv1d(
                in_channels=self.conv_size[0],
                out_channels=self.conv_size[0],
                stride=1, kernel_size=3, padding=1
            ),
            nn.PReLU(),
        )

        self.board_size = board_size

    def forward(self, state):
        res = None
        for s in state:
            current_state = s.unsqueeze(0)
            current_state = current_state + self.get_mask(current_state)

            feature = self.catch(current_state)

            for conv in self.resNet:
                feature = conv(feature) + feature

            if res is None:
                res = self.push(feature)
            else:
                res = torch.cat((res, self.push(feature)))
        return res


class hNet_RL_v1_Sigmoid(hNet_RL_v1):
    def __init__(self, board_size, res_net_layer_number=1):
        super().__init__(board_size=board_size, res_net_layer_number=res_net_layer_number)
        self.push[-1] = nn.Sigmoid()


if __name__ == '__main__':
    _input = torch.randn(2, 9)
    net = hNet_RL_v1(board_size=9)
    output = net(_input)
    print(output.shape)
    print(output)

    _input = torch.randn(2, 9)
    net = hNet_RL_v1_Sigmoid(board_size=9)
    for m in net.modules():
        if isinstance(m, (nn.Conv1d, nn.Linear, nn.Conv2d)):
            nn.init.xavier_uniform_(m.weight)
    output = net(_input)
    print(output.shape)
    print(output)
